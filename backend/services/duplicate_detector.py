"""Duplicate and similar photo detection service."""
import logging
from pathlib import Path

from sqlmodel import Session, select, func

from backend.models.photo import Photo

logger = logging.getLogger(__name__)

# Default phash hamming distance threshold for visual similarity
DEFAULT_PHASH_THRESHOLD = 10


class DuplicateDetector:
    """Detects bitwise duplicates (file_hash) and visual similars (phash)."""

    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory

    def find_duplicates(
        self,
        *,
        dup_type: str = "all",
        threshold: int = DEFAULT_PHASH_THRESHOLD,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """Find duplicate/similar photo groups."""
        session = self._session_factory()
        try:
            groups = []

            if dup_type in ("all", "bitwise"):
                bitwise_groups = self._find_bitwise_duplicates(session)
                groups.extend(bitwise_groups)

            if dup_type in ("all", "visual"):
                visual_groups = self._find_visual_similars(session, threshold)
                groups.extend(visual_groups)

            # Simple pagination
            start = (page - 1) * page_size
            end = start + page_size

            return {
                "groups": groups[start:end],
                "total": len(groups),
                "page": page,
                "page_size": page_size,
            }
        finally:
            session.close()

    def _find_bitwise_duplicates(self, session: Session) -> list[dict]:
        """Find bitwise duplicates grouped by file_hash."""
        from sqlalchemy import text as sa_text

        rows = session.exec(
            select(Photo.file_hash, func.count(Photo.id), func.group_concat(Photo.id))
            .where(
                Photo.file_hash.is_not(None),
                Photo.file_missing == False,  # noqa: E712
            )
            .group_by(Photo.file_hash)
            .having(func.count(Photo.id) > 1)
        ).all()

        groups = []
        for row in rows:
            file_hash = row[0]
            count = row[1]
            photo_ids = [int(x) for x in row[2].split(",")]

            photos = session.exec(
                select(Photo).where(Photo.id.in_(photo_ids))
            ).all()

            groups.append({
                "type": "bitwise",
                "hash": file_hash,
                "photos": [
                    {
                        "id": p.id,
                        "file_path": p.file_path,
                        "file_name": p.file_name,
                        "file_size": p.file_size,
                        "thumbnail_path": p.thumbnail_path,
                    }
                    for p in photos
                ],
                "suggestion": "safe_to_delete",
                "message": "文件内容完全相同，可安全删除冗余副本",
            })

        return groups

    def _find_visual_similars(self, session: Session, threshold: int) -> list[dict]:
        """Find visually similar photos using phash hamming distance.

        Uses a sliding window approach — compares phashes of photos
        that share the first N characters of their phash (a simple
        approximation; a proper DB-backed hamming distance would use
        an extension or in-memory comparison for accuracy).
        """
        photos = session.exec(
            select(Photo).where(
                Photo.phash.is_not(None),
                Photo.file_missing == False,  # noqa: E712
            )
        ).all()

        if len(photos) < 2:
            return []

        groups = []
        processed = set()

        for i in range(len(photos)):
            if photos[i].id in processed:
                continue
            group_members = [photos[i]]
            for j in range(i + 1, len(photos)):
                if photos[j].id in processed:
                    continue
                try:
                    # Compute hamming distance from phash hex strings
                    h1 = int(photos[i].phash, 16) if photos[i].phash else 0
                    h2 = int(photos[j].phash, 16) if photos[j].phash else 0
                    distance = bin(h1 ^ h2).count("1")
                    if distance <= threshold:
                        group_members.append(photos[j])
                except (ValueError, TypeError):
                    continue

            if len(group_members) >= 2:
                for p in group_members:
                    processed.add(p.id)
                groups.append({
                    "type": "visual",
                    "distance": None,
                    "photos": [
                        {
                            "id": p.id,
                            "file_path": p.file_path,
                            "file_name": p.file_name,
                            "file_size": p.file_size,
                            "thumbnail_path": p.thumbnail_path,
                        }
                        for p in group_members
                    ],
                    "suggestion": "review_needed",
                    "message": "视觉相似照片（可能为连拍），请对比后决定",
                })

        return groups
