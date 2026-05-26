"""Hybrid search engine — structured search + NLP entity extraction."""
import logging
import re
from datetime import datetime, timedelta

from sqlmodel import Session, select, func, or_
from sqlalchemy import desc as sa_desc, asc as sa_asc

from backend.models.photo import Photo
from backend.models.tag import Tag
from backend.models.photo_tag import PhotoTag

logger = logging.getLogger(__name__)

SORT_COLUMNS = {
    "date_taken": Photo.date_taken,
    "file_name": Photo.file_name,
    "file_size": Photo.file_size,
    "rating": Photo.rating,
    "created_at": Photo.created_at,
}

# Chinese time entity patterns
_TIME_PATTERNS = [
    (r"去年", lambda: (datetime.utcnow().replace(year=datetime.utcnow().year - 1, month=1, day=1),
                       datetime.utcnow().replace(year=datetime.utcnow().year - 1, month=12, day=31, hour=23, minute=59, second=59))),
    (r"今年", lambda: (datetime.utcnow().replace(month=1, day=1),
                       datetime.utcnow().replace(month=12, day=31, hour=23, minute=59, second=59))),
    (r"上个月", lambda: _relative_month(-1)),
    (r"这个月", lambda: _relative_month(0)),
    (r"最近(\d+)天", lambda m: (datetime.utcnow() - timedelta(days=int(m.group(1))), datetime.utcnow())),
    (r"近(\d+)天", lambda m: (datetime.utcnow() - timedelta(days=int(m.group(1))), datetime.utcnow())),
    (r"(\d{4})年", lambda m: (datetime(int(m.group(1)), 1, 1),
                              datetime(int(m.group(1)), 12, 31, 23, 59, 59))),
    (r"(\d{4})年(\d{1,2})月", lambda m: (datetime(int(m.group(1)), int(m.group(2)), 1),
                                         _last_day_of_month(int(m.group(1)), int(m.group(2))))),
    (r"昨天", lambda: (datetime.utcnow().replace(hour=0, minute=0, second=0) - timedelta(days=1),
                       datetime.utcnow().replace(hour=23, minute=59, second=59) - timedelta(days=1))),
    (r"前天", lambda: (datetime.utcnow().replace(hour=0, minute=0, second=0) - timedelta(days=2),
                       datetime.utcnow().replace(hour=23, minute=59, second=59) - timedelta(days=2))),
]


def _relative_month(offset: int):
    now = datetime.utcnow()
    year = now.year
    month = now.month + offset
    if month < 1:
        year -= 1
        month += 12
    elif month > 12:
        year += 1
        month -= 12
    return (datetime(year, month, 1),
            _last_day_of_month(year, month))


def _last_day_of_month(year: int, month: int):
    if month == 12:
        return datetime(year, 12, 31, 23, 59, 59)
    return datetime(year, month + 1, 1) - timedelta(seconds=1)


def extract_time_entities(query: str) -> dict:
    """Extract time range from Chinese natural language query."""
    for pattern, builder in _TIME_PATTERNS:
        m = re.search(pattern, query)
        if m:
            try:
                date_from, date_to = builder(m) if callable(builder) else builder()
                return {"date_from": date_from, "date_to": date_to}
            except Exception:
                continue
    return {}


def extract_tag_entities(query: str, session: Session) -> list[int]:
    """Extract tag IDs from query text by matching tag names (zh/en)."""
    tags = session.exec(select(Tag)).all()
    matched_ids = []
    for tag in tags:
        if tag.name and tag.name in query:
            matched_ids.append(tag.id)
        elif tag.name_zh and tag.name_zh in query:
            matched_ids.append(tag.id)
    return matched_ids


def structured_search(
    session: Session,
    *,
    filters: dict | None = None,
    logic: str = "AND",
    sort_by: str = "date_taken",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Photo], int]:
    """Perform structured multi-condition search."""
    base = select(Photo).where(Photo.file_missing == False)  # noqa: E712
    filters = filters or {}
    conditions = []

    if filters.get("library_id"):
        conditions.append(Photo.library_source_id == filters["library_id"])
    if filters.get("date_from"):
        conditions.append(Photo.date_taken >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(Photo.date_taken <= filters["date_to"])
    if filters.get("camera_make"):
        conditions.append(Photo.camera_make == filters["camera_make"])
    if filters.get("camera_model"):
        conditions.append(Photo.camera_model == filters["camera_model"])
    if filters.get("lens_model"):
        conditions.append(Photo.lens_model == filters["lens_model"])
    if filters.get("iso"):
        conditions.append(Photo.iso == filters["iso"])
    if filters.get("f_number"):
        conditions.append(Photo.f_number == filters["f_number"])
    if filters.get("focal_length"):
        conditions.append(Photo.focal_length == filters["focal_length"])
    if filters.get("exposure_time"):
        conditions.append(Photo.exposure_time == filters["exposure_time"])
    if filters.get("rating_min"):
        conditions.append(Photo.rating >= filters["rating_min"])
    if filters.get("is_favorite"):
        conditions.append(Photo.is_favorite == True)  # noqa: E712
    if filters.get("has_gps"):
        conditions.append(Photo.gps_latitude.is_not(None))
    if filters.get("file_name"):
        conditions.append(Photo.file_name.ilike(f"%{filters['file_name']}%"))

    # Tag filtering via subquery
    tag_ids = filters.get("tag_ids", [])
    if tag_ids:
        subq = (
            select(PhotoTag.photo_id)
            .where(PhotoTag.tag_id.in_(tag_ids))
            .group_by(PhotoTag.photo_id)
        )
        if logic == "AND":
            subq = subq.having(func.count(PhotoTag.tag_id) == len(tag_ids))
        conditions.append(Photo.id.in_(subq))

    if filters.get("exclude_tag_ids"):
        subq = select(PhotoTag.photo_id).where(
            PhotoTag.tag_id.in_(filters["exclude_tag_ids"])
        )
        conditions.append(~Photo.id.in_(subq))

    # Apply logic
    if conditions:
        if logic == "OR":
            base = base.where(or_(*conditions))
        else:
            base = base.where(*conditions)

    # Count
    count_q = select(func.count()).select_from(base.subquery())
    total = session.exec(count_q).one()

    # Sort
    sort_col = SORT_COLUMNS.get(sort_by, Photo.date_taken)
    sort_fn = sa_desc if sort_order == "desc" else sa_asc
    base = base.order_by(sort_fn(sort_col))

    # Page
    photos = session.exec(
        base.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return list(photos), total


def hybrid_search(
    session: Session,
    query: str,
    *,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[tuple[Photo, float]] | list[Photo], int]:
    """Hybrid search: NLP entity extraction + CLIP semantic vector search + structured filter.

    Returns list of (Photo, similarity_score) tuples when CLIP is available,
    falling back to plain Photo list when CLIP is unavailable.
    """
    filters = {}

    # Step 1: Extract time entities
    time_range = extract_time_entities(query)
    filters.update(time_range)

    # Step 2: Extract tag entities
    tag_ids = extract_tag_entities(query, session)
    if tag_ids:
        filters["tag_ids"] = tag_ids

    # Step 3: CLIP semantic vector search (S3)
    clip_photo_ids: set[int] | None = None
    clip_scores: dict[int, float] = {}
    try:
        from backend.services.clip_service import ClipService

        clip = ClipService()
        text_emb = clip.generate_text_embedding(query)
        if text_emb is not None:
            vector_results = clip.search_similar(text_emb, session, top_k=200)
            if vector_results:
                clip_photo_ids = {pid for pid, _ in vector_results}
                clip_scores = dict(vector_results)
    except Exception as e:
        logger.warning(f"CLIP search failed, falling back to structured: {e}")

    # Step 4: If CLIP matched, intersect with structured filters
    if clip_photo_ids:
        # Apply structured filters on the CLIP candidate set
        base = select(Photo).where(
            Photo.file_missing == False,  # noqa: E712
            Photo.id.in_(clip_photo_ids),
        )

        conditions = _build_filter_conditions(filters)
        if conditions:
            base = base.where(*conditions)

        count_q = select(func.count()).select_from(base.subquery())
        total = session.exec(count_q).one()

        photos = session.exec(base.all()).all()

        # Sort by similarity score descending
        photos_with_scores = [(p, clip_scores.get(p.id, 0.0)) for p in photos]
        photos_with_scores.sort(key=lambda x: x[1], reverse=True)

        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        page_photos = photos_with_scores[start:end]

        return page_photos, total

    # Step 5: Fallback — no CLIP, apply structured only
    if not filters:
        keyword = query.strip()
        if keyword:
            filters["file_name"] = keyword

    photos, total = structured_search(
        session,
        filters=filters or None,
        logic="AND",
        sort_by="date_taken",
        sort_order="desc",
        page=page,
        page_size=page_size,
    )
    return photos, total


def _build_filter_conditions(filters: dict) -> list:
    """Build SQLAlchemy conditions from structured filters dict."""
    from sqlmodel import or_
    from backend.models.photo_tag import PhotoTag

    conditions = []
    if filters.get("date_from"):
        conditions.append(Photo.date_taken >= filters["date_from"])
    if filters.get("date_to"):
        conditions.append(Photo.date_taken <= filters["date_to"])
    if filters.get("camera_make"):
        conditions.append(Photo.camera_make == filters["camera_make"])
    if filters.get("camera_model"):
        conditions.append(Photo.camera_model == filters["camera_model"])
    if filters.get("lens_model"):
        conditions.append(Photo.lens_model == filters["lens_model"])
    if filters.get("rating_min"):
        conditions.append(Photo.rating >= filters["rating_min"])
    if filters.get("is_favorite"):
        conditions.append(Photo.is_favorite == True)  # noqa: E712
    if filters.get("has_gps"):
        conditions.append(Photo.gps_latitude.is_not(None))
    if filters.get("file_name"):
        conditions.append(Photo.file_name.ilike(f"%{filters['file_name']}%"))

    tag_ids = filters.get("tag_ids", [])
    if tag_ids:
        subq = (
            select(PhotoTag.photo_id)
            .where(PhotoTag.tag_id.in_(tag_ids))
            .group_by(PhotoTag.photo_id)
            .having(func.count(PhotoTag.tag_id) == len(tag_ids))
        )
        conditions.append(Photo.id.in_(subq))

    return conditions
