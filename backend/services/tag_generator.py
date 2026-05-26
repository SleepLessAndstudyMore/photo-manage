"""YOLOv8 tag generation service."""
import logging
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from backend.data.coco_classes import (
    COCO_EN_TO_ZH, COCO_CLASS_NAMES,
    DEFAULT_CONFIDENCE_THRESHOLD,
)
from backend.models.photo import Photo
from backend.models.tag import Tag
from backend.models.photo_tag import PhotoTag
from backend.tasks.task_manager import task_manager

logger = logging.getLogger(__name__)


class TagGenerator:
    """Generates YOLOv8 auto-tags for photos."""

    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory
        self._model = None

    def _lazy_load_model(self):
        if self._model is None:
            try:
                from ultralytics import YOLO
                self._model = YOLO("yolov8n.pt")
                logger.info("YOLOv8 model loaded (yolov8n.pt)")
            except Exception as e:
                logger.warning(f"Failed to load YOLOv8 model: {e}, tags will not be generated")
                self._model = None
        return self._model

    def generate_tags(self, task_info, photo_ids: list[int], source_paths: list[str], is_videos: list[bool]):
        """Generate YOLOv8 tags for a batch of photos. Runs in background thread."""
        model = self._lazy_load_model()
        if model is None:
            logger.warning("YOLOv8 model unavailable, skipping tag generation")
            return

        session = self._session_factory()
        try:
            # Pre-fetch non-video image paths
            image_paths = []
            image_photo_ids = []
            for pid, spath, is_v in zip(photo_ids, source_paths, is_videos):
                if not is_v:
                    image_paths.append(spath)
                    image_photo_ids.append(pid)

            if not image_paths:
                return

            total = len(image_paths)
            batch_size = 16

            _ensure_tags_exist(session)
            session.commit()

            logger.info(f"Generating YOLOv8 tags for {total} images")
            task_manager.update_progress(task_info.id, 0.0, f"YOLOv8 标签生成: 0/{total}")

            for i in range(0, total, batch_size):
                if task_info.is_cancelled:
                    return

                batch_paths = image_paths[i : i + batch_size]
                batch_ids = image_photo_ids[i : i + batch_size]

                try:
                    results = model(batch_paths, verbose=False)
                    for photo_id, result in zip(batch_ids, results):
                        _save_detections(session, photo_id, result)
                except Exception as e:
                    logger.warning(f"YOLOv8 batch inference error: {e}")

                if (i // batch_size) % 4 == 0:
                    session.commit()

                progress = min((i + batch_size) / max(total, 1), 0.95)
                task_manager.update_progress(
                    task_info.id, progress,
                    f"YOLOv8 标签生成: {min(i + batch_size, total)}/{total}",
                )

            session.commit()

            # Update tag photo counts
            _update_tag_counts(session)
            session.commit()

            logger.info("YOLOv8 tag generation complete")
            task_manager.update_progress(task_info.id, 1.0, "标签生成完成")
        finally:
            session.close()

    def generate_tags_for_photo(self, file_path: str) -> list[dict]:
        """Generate tags for a single photo file (synchronous)."""
        model = self._lazy_load_model()
        if model is None:
            return []

        try:
            results = model([file_path], verbose=False)
            detections = []
            if results and results[0].boxes is not None:
                for box in results[0].boxes:
                    cls_id = int(box.cls[0].item())
                    confidence = float(box.conf[0].item())
                    if cls_id < len(COCO_CLASS_NAMES):
                        detections.append({
                            "class_id": cls_id,
                            "name_en": list(COCO_CLASS_NAMES)[cls_id],
                            "confidence": confidence,
                        })
            return detections
        except Exception as e:
            logger.warning(f"Single photo tag generation error: {e}")
            return []


def _ensure_tags_exist(session: Session):
    """Ensure all COCO 80 classes exist as Tag rows."""
    from backend.data.coco_classes import COCO_CLASSES_EN, COCO_EN_TO_ZH

    existing = {t.name for t in session.exec(select(Tag)).all()}
    for name_en in COCO_CLASSES_EN:
        if name_en not in existing:
            tag = Tag(
                name=name_en,
                name_zh=COCO_EN_TO_ZH.get(name_en),
                type="auto",
                photo_count=0,
            )
            session.add(tag)


def _save_detections(session: Session, photo_id: int, result):
    """Save YOLOv8 detections as PhotoTag rows. Skip if below threshold."""
    from backend.data.coco_classes import COCO_CLASSES_EN

    if result.boxes is None:
        return

    existing_tag_map = {}
    tags = session.exec(select(Tag)).all()
    for t in tags:
        existing_tag_map[t.name] = t.id

    seen_tag_ids = set()
    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        confidence = float(box.conf[0].item())
        if confidence < DEFAULT_CONFIDENCE_THRESHOLD:
            continue
        if cls_id >= len(COCO_CLASSES_EN):
            continue

        name_en = COCO_CLASSES_EN[cls_id]
        tag_id = existing_tag_map.get(name_en)
        if tag_id is None:
            continue
        if tag_id in seen_tag_ids:
            continue  # deduplicate per photo
        seen_tag_ids.add(tag_id)

        existing_pt = session.exec(
            select(PhotoTag).where(
                PhotoTag.photo_id == photo_id,
                PhotoTag.tag_id == tag_id,
            )
        ).first()
        if existing_pt:
            continue

        pt = PhotoTag(
            photo_id=photo_id,
            tag_id=tag_id,
            confidence=confidence,
            source="auto",
        )
        session.add(pt)


def _update_tag_counts(session: Session):
    """Refresh tag.photo_count based on actual PhotoTag rows."""
    from sqlmodel import func

    count_rows = session.exec(
        select(PhotoTag.tag_id, func.count(PhotoTag.photo_id))
        .group_by(PhotoTag.tag_id)
    ).all()
    tag_counts = {row[0]: row[1] for row in count_rows}

    for tag in session.exec(select(Tag)).all():
        tag.photo_count = tag_counts.get(tag.id, 0)
        session.add(tag)
