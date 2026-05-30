from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # 应用基础
    APP_NAME: str = "PhotoManager"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # 目录
    BASE_DIR: Path = BASE_DIR
    THUMBNAIL_DIR: Path = BASE_DIR / "thumbnails"
    DATA_DIR: Path = BASE_DIR / "data"
    MODEL_DIR: Path = BASE_DIR / "models"
    FRONTEND_DIST: Path = BASE_DIR / "frontend" / "dist"
    ASSETS_DIR: Path = BASE_DIR / "assets"

    # 数据库
    DB_PATH: Path = DATA_DIR / "photo_manager.db"
    DATABASE_URL: str = "sqlite:///./data/photo_manager.db"

    # 缩略图
    THUMBNAIL_SMALL_SIZE: tuple[int, int] = (300, 300)
    THUMBNAIL_PREVIEW_SIZE: tuple[int, int] = (1200, 1200)
    THUMBNAIL_QUALITY: int = 80

    # 扫描
    SCAN_BATCH_SIZE: int = 100
    SCAN_INTERVAL: int = 300

    # 分页
    PAGE_SIZE_DEFAULT: int = 50
    PAGE_SIZE_MAX: int = 200

    # HuggingFace (CLIP 模型下载)
    HF_TOKEN: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
