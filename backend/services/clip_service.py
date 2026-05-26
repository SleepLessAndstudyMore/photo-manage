"""CLIP vector service for semantic search."""
import logging
import threading
from pathlib import Path

import numpy as np
from PIL import Image
from sqlmodel import Session, select

from backend.models.photo_embedding import PhotoEmbedding
from backend.tasks.task_manager import task_manager

logger = logging.getLogger(__name__)

SIMILARITY_CUTOFF = 0.15

# Shared model state (thread-safe)
_model = None
_model_lock = threading.Lock()
_model_load_attempted = False


def _try_load_model(timeout: float = 30.0, max_retries: int = 3) -> bool:
    """Try to load the CLIP model with retry support.

    Retries up to `max_retries` times on network failure.
    Returns True if loaded successfully, False if failed or timed out.
    Only attempts download once; subsequent calls return immediately.
    """
    global _model, _model_load_attempted

    if _model is not None:
        return True
    if _model_load_attempted:
        return False  # Already tried and failed

    with _model_lock:
        if _model is not None:
            return True
        if _model_load_attempted:
            return False

        _model_load_attempted = True  # Mark before attempt to avoid re-entry

        for attempt in range(1, max_retries + 1):
            result = [None]
            exception = [None]
            event = threading.Event()

            def _load():
                try:
                    from sentence_transformers import SentenceTransformer
                    result[0] = SentenceTransformer("clip-ViT-B-32")
                    logger.info("CLIP model loaded (clip-ViT-B-32)")
                except Exception as e:
                    exception[0] = e
                finally:
                    event.set()

            t = threading.Thread(target=_load, daemon=True)
            t.start()
            loaded = event.wait(timeout=timeout)

            if loaded and result[0] is not None:
                _model = result[0]
                return True
            elif loaded and exception[0] is not None:
                if attempt < max_retries:
                    logger.warning(
                        f"CLIP model download attempt {attempt}/{max_retries} failed: "
                        f"{exception[0]}. Retrying..."
                    )
                    import time
                    time.sleep(2)
                    continue
                logger.warning(
                    f"Failed to load CLIP model after {max_retries} attempts: "
                    f"{exception[0]}. Semantic search will be unavailable."
                )
            else:
                if attempt < max_retries:
                    logger.warning(
                        f"CLIP model download timed out after {timeout}s "
                        f"(attempt {attempt}/{max_retries}). Retrying..."
                    )
                    import time
                    time.sleep(2)
                    continue
                logger.warning(
                    f"CLIP model download timed out after {max_retries} attempts. "
                    "Semantic search will be unavailable. "
                    "Run offline: python -c \"from sentence_transformers import "
                    "SentenceTransformer; SentenceTransformer('clip-ViT-B-32')\""
                )
            return False


def _get_model():
    """Get the CLIP model, attempting lazy load if not yet tried."""
    if _model is not None:
        return _model
    if _model_load_attempted:
        return None
    _try_load_model()
    return _model


def reset_clip_model():
    """Reset model load state so next call retries loading."""
    global _model, _model_load_attempted
    with _model_lock:
        _model = None
        _model_load_attempted = False


class ClipService:
    """CLIP-based image and text embedding generation & search."""

    def __init__(self, db_session_factory=None):
        self._session_factory = db_session_factory

    # -- Public helpers used by search (no session factory needed) --

    def generate_embedding(self, image_path: str) -> bytes | None:
        """Generate CLIP embedding for a single image. Returns raw float32 bytes."""
        model = _get_model()
        if model is None:
            return None
        try:
            embedding = model.encode(Image.open(image_path))
            return np.array(embedding, dtype=np.float32).tobytes()
        except Exception as e:
            logger.warning(f"CLIP encoding failed for {image_path}: {e}")
            return None

    def generate_text_embedding(self, text: str) -> np.ndarray | None:
        """Generate CLIP embedding for a text query."""
        model = _get_model()
        if model is None:
            return None
        try:
            embedding = model.encode(text)
            return np.array(embedding, dtype=np.float32)
        except Exception as e:
            logger.warning(f"CLIP text encoding failed: {e}")
            return None

    def search_similar(
        self, text_embedding: np.ndarray, session: Session, top_k: int = 200
    ) -> list[tuple[int, float]]:
        """Search for similar photos by cosine similarity.

        Returns list of (photo_id, similarity_score) sorted descending.
        """
        rows = session.exec(select(PhotoEmbedding)).all()
        if not rows:
            return []

        vectors = np.array([
            np.frombuffer(r.embedding_blob, dtype=np.float32)
            for r in rows
        ])
        photo_ids = np.array([r.photo_id for r in rows])

        query_norm = text_embedding / (np.linalg.norm(text_embedding) + 1e-8)

        norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-8
        vectors_norm = vectors / norms
        similarities = vectors_norm @ query_norm

        valid = similarities >= SIMILARITY_CUTOFF
        if not np.any(valid):
            top_indices = np.argsort(similarities)[-top_k:][::-1]
        else:
            valid_indices = np.where(valid)[0]
            if len(valid_indices) > top_k:
                top_order = np.argsort(similarities[valid_indices])[-top_k:][::-1]
                top_indices = valid_indices[top_order]
            else:
                top_order = np.argsort(similarities[valid_indices])[::-1]
                top_indices = valid_indices[top_order]

        results = [(int(photo_ids[i]), float(similarities[i])) for i in top_indices]
        return results

    # -- Background task (needs session factory) --

    def generate_all_embeddings(
        self, task_info,
        photo_ids: list[int] | None = None,
        source_paths: list[str] | None = None,
        is_videos: list[bool] | None = None,
    ):
        """Background task: generate CLIP embeddings for photos.

        If photo_ids/source_paths/is_videos are passed, process only those (from scan).
        Otherwise, query all photos that have no PhotoEmbedding row.
        """
        model = _get_model()
        if model is None:
            logger.warning("CLIP model unavailable, skipping embedding generation")
            return

        session = self._session_factory()
        try:
            if photo_ids is not None and source_paths is not None:
                image_paths = []
                image_ids = []
                for pid, spath, is_v in zip(photo_ids, source_paths, is_videos or []):
                    if not is_v:
                        image_paths.append(spath)
                        image_ids.append(pid)
            else:
                # Full scan: find all image photos without existing embeddings
                from backend.models.photo import Photo
                all_photos = session.exec(
                    select(Photo).where(
                        Photo.file_missing == False,  # noqa: E712
                        Photo.is_video == False,  # noqa: E712
                    )
                ).all()
                existing_ids = set(
                    row[0] for row in session.exec(
                        select(PhotoEmbedding.photo_id).distinct()
                    ).all()
                )
                targets = [(p.id, p.file_path) for p in all_photos if p.id not in existing_ids]
                image_ids = [t[0] for t in targets]
                image_paths = [t[1] for t in targets]

            if not image_paths:
                return

            total = len(image_paths)
            logger.info(f"Generating CLIP embeddings for {total} images")
            task_manager.update_progress(
                task_info.id, 0.0, f"CLIP 向量生成: 0/{total}"
            )

            for i, (pid, spath) in enumerate(zip(image_ids, image_paths)):
                if task_info.is_cancelled:
                    return

                try:
                    embedding_bytes = self.generate_embedding(spath)
                    if embedding_bytes is None:
                        continue

                    existing = session.get(PhotoEmbedding, pid)
                    if existing:
                        existing.embedding_blob = embedding_bytes
                        session.add(existing)
                    else:
                        emb = PhotoEmbedding(
                            photo_id=pid,
                            embedding_blob=embedding_bytes,
                            embedding_model="clip-vit-b-32",
                        )
                        session.add(emb)

                    if i % 20 == 0:
                        session.commit()
                except Exception as e:
                    logger.warning(f"CLIP embedding error for {spath}: {e}")
                    session.rollback()

                if i % 10 == 0:
                    task_manager.update_progress(
                        task_info.id,
                        min((i + 1) / max(total, 1), 0.95),
                        f"CLIP 向量生成: {i + 1}/{total}",
                    )

            session.commit()
            logger.info("CLIP embedding generation complete")
            task_manager.update_progress(task_info.id, 1.0, "向量生成完成")
        finally:
            session.close()
