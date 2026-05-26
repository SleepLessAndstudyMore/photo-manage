import logging
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageOps

from config.settings import settings

logger = logging.getLogger(__name__)

FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None
FFPROBE_AVAILABLE = shutil.which("ffprobe") is not None


class ThumbnailGenerator:
    def __init__(self, thumbnail_dir: Path | None = None):
        self.thumbnail_dir = thumbnail_dir or settings.THUMBNAIL_DIR
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def generate_small(self, photo_id: int, source_path: str, is_video: bool = False) -> dict:
        output_path = self._get_output_path(photo_id, "small")
        if is_video:
            w, h = self._generate_video_thumbnail(source_path, output_path, 300)
        else:
            w, h = self._generate_image_thumbnail(source_path, output_path, 300)
        return {
            "thumbnail_path": output_path.name,
            "thumbnail_width": w,
            "thumbnail_height": h,
        }

    def generate_preview(self, photo_id: int, source_path: str, is_video: bool = False) -> dict:
        output_path = self._get_output_path(photo_id, "preview")
        if is_video:
            w, h = self._generate_video_thumbnail(source_path, output_path, 1200)
        else:
            w, h = self._generate_image_thumbnail(source_path, output_path, 1200)
        return {
            "preview_path": output_path.name,
            "preview_width": w,
            "preview_height": h,
        }

    def generate_both(self, photo_id: int, source_path: str, is_video: bool = False) -> dict:
        small = self.generate_small(photo_id, source_path, is_video)
        preview = self.generate_preview(photo_id, source_path, is_video)
        result = {}
        result.update(small)
        result.update(preview)
        return result

    @staticmethod
    def generate_for_photos(
        task_info,  # TaskInfo
        photo_ids: list[int],
        source_paths: list[str],
        is_videos: list[bool],
        db_session_factory,
    ):
        from backend.models.photo import Photo
        from sqlmodel import select

        generator = ThumbnailGenerator()
        total = len(photo_ids)
        for idx, (pid, src_path, is_vid) in enumerate(zip(photo_ids, source_paths, is_videos)):
            if task_info.is_cancelled:
                return
            try:
                result = generator.generate_both(pid, src_path, is_vid)
                session = db_session_factory()
                try:
                    photo = session.exec(select(Photo).where(Photo.id == pid)).first()
                    if photo:
                        photo.thumbnail_path = result.get("thumbnail_path")
                        photo.thumbnail_width = result.get("thumbnail_width")
                        photo.thumbnail_height = result.get("thumbnail_height")
                        photo.preview_path = result.get("preview_path")
                        session.add(photo)
                        session.commit()
                finally:
                    session.close()
                from backend.tasks.task_manager import task_manager
                task_manager.update_progress(
                    task_info.id, (idx + 1) / total, f"缩略图 {idx + 1}/{total}"
                )
            except Exception as e:
                logger.warning(f"Thumbnail failed for photo {pid} ({src_path}): {e}")

    def _generate_image_thumbnail(
        self, source_path: str, output_path: Path, max_side: int, quality: int = 80
    ) -> tuple[int | None, int | None]:
        try:
            img = Image.open(source_path)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((max_side, max_side), Image.LANCZOS)
            rgb = img.convert("RGB")
            rgb.save(output_path, "JPEG", quality=quality)
            w, h = rgb.size
            return w, h
        except Exception as e:
            logger.warning(f"Image thumbnail failed for {source_path}: {e}")
            return None, None

    def _generate_video_thumbnail(
        self, source_path: str, output_path: Path, max_side: int
    ) -> tuple[int | None, int | None]:
        if not FFMPEG_AVAILABLE:
            logger.warning("ffmpeg not available, skipping video thumbnail")
            return None, None

        seek_time = self._get_seek_time(source_path)
        try:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(seek_time),
                "-i", source_path,
                "-vframes", "1",
                "-vf", f"scale={max_side}:{max_side}:force_original_aspect_ratio=decrease",
                "-q:v", "5",
                str(output_path),
            ]
            subprocess.run(cmd, capture_output=True, timeout=30, check=True)
            if output_path.exists():
                try:
                    img = Image.open(output_path)
                    w, h = img.size
                    img.close()
                    return w, h
                except Exception:
                    pass
            return None, None
        except Exception as e:
            logger.warning(f"Video thumbnail failed for {source_path}: {e}")
            return None, None

    @staticmethod
    def _get_seek_time(source_path: str) -> float:
        if not FFPROBE_AVAILABLE:
            return 1.0
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                source_path,
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
            duration = float(result.stdout.strip())
            if duration > 0:
                return max(duration / 4, 0.5)
        except Exception:
            pass
        return 1.0

    def _get_output_path(self, photo_id: int, suffix: str) -> Path:
        return self.thumbnail_dir / f"{photo_id}_{suffix}.jpg"
