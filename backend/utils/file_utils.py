import hashlib
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS: set[str] = {
    '.jpg', '.jpeg', '.png', '.heic', '.heif', '.bmp', '.tiff', '.tif', '.webp'
}

SUPPORTED_VIDEO_EXTENSIONS: set[str] = {'.mp4', '.mov', '.avi'}

SUPPORTED_EXTENSIONS: set[str] = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS

SKIP_DIR_NAMES: set[str] = {
    '$RECYCLE.BIN', 'System Volume Information', '.thumbnails',
    '__MACOSX', '.DS_Store', 'Thumbs.db',
}


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def compute_file_hash(filepath: str | Path, algorithm: str = "md5") -> str | None:
    try:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, ValueError):
        return None


def is_supported_image(filepath: str | Path) -> bool:
    return Path(filepath).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def is_supported_video(filepath: str | Path) -> bool:
    return Path(filepath).suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS


def is_supported_file(filepath: str | Path) -> bool:
    return Path(filepath).suffix.lower() in SUPPORTED_EXTENSIONS


def get_file_size_mb(filepath: str | Path) -> float:
    try:
        return Path(filepath).stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0
