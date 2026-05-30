import logging
import os
import time
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select, func

from backend.models.photo import Photo
from backend.models.library_source import LibrarySource
from backend.services.exif_parser import ExifParser
from backend.services.thumbnail import ThumbnailGenerator
from backend.tasks.task_manager import task_manager, TaskType
from backend.utils.file_utils import (
    is_supported_file, is_supported_image, is_supported_video,
    compute_file_hash, SKIP_DIR_NAMES,
)
from PIL import Image, ImageOps
import imagehash

logger = logging.getLogger(__name__)


class Scanner:
    def __init__(self, db_session_factory):
        self._session_factory = db_session_factory

    def scan_library(self, task_info, library_id: int, full_scan: bool = False):
        session = self._session_factory()
        try:
            library = session.exec(
                select(LibrarySource).where(LibrarySource.id == library_id)
            ).first()
            if library is None:
                raise ValueError(f"Library {library_id} not found")

            # Reset stuck scanning state
            if library.scan_status == "scanning":
                library.scan_status = "idle"
                session.add(library)
                session.commit()

            library.scan_status = "scanning"
            session.add(library)
            session.commit()

            root_path = Path(library.path)
            files = self._collect_files(root_path)
            total = len(files)

            new_photo_ids = []
            new_source_paths = []
            new_is_videos = []
            processed = 0

            for file_path in files:
                if task_info.is_cancelled:
                    break

                try:
                    photo = self._process_file(file_path, library_id, session, full_scan)
                    if photo:
                        new_photo_ids.append(photo.id)
                        new_source_paths.append(str(file_path))
                        new_is_videos.append(photo.is_video)
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
                    session.rollback()
                    session.close()
                    session = self._session_factory()

                processed += 1
                if processed % 10 == 0:
                    task_manager.update_progress(
                        task_info.id,
                        processed / (total + 1),
                        f"扫描 {processed}/{total}",
                    )
                    if processed % 100 == 0:
                        session.commit()

            session.commit()

            # Consistency check: find missing files
            task_manager.update_progress(task_info.id, 0.9, "一致性校验中...")
            self._check_missing_files(library_id, session, task_info)

            # Update library stats
            photo_count = session.exec(
                select(func.count(Photo.id)).where(
                    Photo.library_source_id == library_id,
                    Photo.file_missing == False,  # noqa: E712
                )
            ).one()
            library.photo_count = photo_count
            library.last_scan_at = datetime.utcnow()
            library.scan_status = "completed"
            session.add(library)
            session.commit()

            # Submit thumbnail generation task
            if new_photo_ids:
                task_manager.create_and_run(
                    TaskType.THUMBNAIL,
                    ThumbnailGenerator.generate_for_photos,
                    args=(new_photo_ids, new_source_paths, new_is_videos, self._session_factory),
                    library_id=library_id,
                )

            # Submit YOLOv8 auto-tagging task
            if new_photo_ids:
                from backend.services.tag_generator import TagGenerator
                tag_gen = TagGenerator(self._session_factory)
                task_manager.create_and_run(
                    TaskType.TAG,
                    tag_gen.generate_tags,
                    args=(new_photo_ids, new_source_paths, new_is_videos),
                    library_id=library_id,
                )

            # Submit CLIP embedding generation (S3)
            if new_photo_ids:
                from backend.services.clip_service import ClipService
                clip_svc = ClipService(self._session_factory)
                task_manager.create_and_run(
                    TaskType.CLIP,
                    clip_svc.generate_all_embeddings,
                    args=(new_photo_ids, new_source_paths, new_is_videos),
                    library_id=library_id,
                )

            # Submit face detection (S3)
            if new_photo_ids:
                from backend.services.face_service import FaceService
                face_svc = FaceService(self._session_factory)
                task_manager.create_and_run(
                    TaskType.FACE_DETECT,
                    face_svc.detect_all_faces,
                    args=(new_photo_ids, new_source_paths, new_is_videos),
                    library_id=library_id,
                )

            # Submit phash computation for existing photos missing phash
            from backend.services.duplicate_detector import DuplicateDetector
            dup_detector = DuplicateDetector(self._session_factory)
            task_manager.create_and_run(
                TaskType.DUPLICATE,
                dup_detector.compute_phash_batch,
                args=(library_id,),
                library_id=library_id,
            )
        finally:
            session.close()

    def check_consistency(self, task_info, library_id: int):
        session = self._session_factory()
        try:
            task_manager.update_progress(task_info.id, 0.1, "一致性校验中...")
            self._check_missing_files(library_id, session, task_info)
            session.commit()
        finally:
            session.close()

    def _collect_files(self, root_path: Path) -> list[Path]:
        files = []
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in SKIP_DIR_NAMES
            ]
            for fname in filenames:
                if not fname.startswith("."):
                    fpath = Path(dirpath) / fname
                    if is_supported_file(fpath):
                        files.append(fpath)
        return files

    def _process_file(
        self, file_path: Path, library_id: int, session: Session, full_scan: bool
    ) -> Photo | None:
        file_path_str = str(file_path)
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_mtime = file_stat.st_mtime
        except OSError:
            return None

        # Incremental scan: check if already indexed and unchanged
        existing = session.exec(
            select(Photo).where(
                Photo.file_path == file_path_str,
                Photo.library_source_id == library_id,
            )
        ).first()

        if existing and not full_scan:
            if (existing.file_size == file_size
                    and existing.file_modified_time == file_mtime):
                return None  # Unchanged, skip

        is_vid = is_supported_video(file_path)
        is_img = is_supported_image(file_path)

        metadata = {}
        if is_img:
            metadata = ExifParser.parse(file_path)

        if existing:
            photo = existing
            # 文件被修改过，清空缩略图路径以触发重新生成
            if photo.file_modified_time != file_mtime:
                photo.thumbnail_path = None
                photo.thumbnail_width = None
                photo.thumbnail_height = None
                photo.preview_path = None
        else:
            photo = Photo(
                library_source_id=library_id,
                file_path=file_path_str,
                file_name=file_path.name,
                file_size=file_size,
                file_modified_time=file_mtime,
                file_hash=compute_file_hash(file_path),
                is_video=is_vid,
            )
            session.add(photo)
            session.flush()  # Get photo.id

        photo.date_taken = metadata.get("date_taken") or datetime.fromtimestamp(file_mtime)
        photo.date_modified = metadata.get("date_modified")
        photo.camera_make = metadata.get("camera_make")
        photo.camera_model = metadata.get("camera_model")
        photo.lens_model = metadata.get("lens_model")
        photo.f_number = metadata.get("f_number")
        photo.exposure_time = metadata.get("exposure_time")
        photo.iso = metadata.get("iso")
        photo.focal_length = metadata.get("focal_length")
        photo.gps_latitude = metadata.get("gps_latitude")
        photo.gps_longitude = metadata.get("gps_longitude")
        photo.orientation = metadata.get("orientation", 1)
        photo.width = metadata.get("width")
        photo.height = metadata.get("height")
        photo.file_missing = False

        # 为图片计算感知哈希（phash），用于视觉相似检测
        if is_img and not photo.phash:
            photo.phash = self._compute_phash(file_path)

        photo.updated_at = datetime.utcnow()
        return photo

    def _compute_phash(self, file_path: Path) -> str | None:
        """计算图片的感知哈希，用于视觉相似照片检测。"""
        try:
            img = Image.open(file_path)
            img = ImageOps.exif_transpose(img)
            phash = imagehash.phash(img)
            return str(phash)
        except Exception as e:
            logger.warning(f"感知哈希计算失败: {file_path}: {e}")
            return None

    def _check_missing_files(self, library_id: int, session: Session, task_info):
        photos = session.exec(
            select(Photo).where(
                Photo.library_source_id == library_id,
                Photo.file_missing == False,  # noqa: E712
            )
        ).all()

        total = len(photos)
        for i, photo in enumerate(photos):
            if task_info and task_info.is_cancelled:
                return
            if not os.path.exists(photo.file_path):
                photo.file_missing = True
                session.add(photo)
            if i % 100 == 0 and task_info:
                task_manager.update_progress(
                    task_info.id,
                    0.9 + 0.1 * (i / max(total, 1)),
                    f"一致性校验 {i}/{total}",
                )
