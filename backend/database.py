import logging
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

from config.settings import settings
from backend.models import *  # noqa: F401 F403 — ensure all models register on metadata

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False, "timeout": 30},
)


def init_db() -> None:
    """Create all tables, enable WAL mode, create indexes."""
    SQLModel.metadata.create_all(engine)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA busy_timeout=30000"))  # 30s retry on lock
        conn.execute(text("PRAGMA cache_size=-8000"))  # ~8MB cache
        # S1 migration: add file_modified_time column
        try:
            conn.execute(
                text("ALTER TABLE photo ADD COLUMN file_modified_time FLOAT")
            )
        except Exception:
            pass  # Column already exists
        # S2 migration: ensure name_zh column on tag table
        try:
            conn.execute(
                text("ALTER TABLE tag ADD COLUMN name_zh VARCHAR")
            )
        except Exception:
            pass
        # Create indexes for common queries
        _create_index_if_not_exists(conn, "idx_photo_date_taken", "CREATE INDEX IF NOT EXISTS idx_photo_date_taken ON photo(date_taken)")
        _create_index_if_not_exists(conn, "idx_photo_library", "CREATE INDEX IF NOT EXISTS idx_photo_library ON photo(library_source_id)")
        _create_index_if_not_exists(conn, "idx_photo_favorite", "CREATE INDEX IF NOT EXISTS idx_photo_favorite ON photo(is_favorite)")
        _create_index_if_not_exists(conn, "idx_photo_file_missing", "CREATE INDEX IF NOT EXISTS idx_photo_file_missing ON photo(file_missing)")
        _create_index_if_not_exists(conn, "idx_photo_gps", "CREATE INDEX IF NOT EXISTS idx_photo_gps ON photo(gps_latitude, gps_longitude)")
        _create_index_if_not_exists(conn, "idx_photo_file_path", "CREATE INDEX IF NOT EXISTS idx_photo_file_path ON photo(file_path)")
        _create_index_if_not_exists(conn, "idx_photo_tag_photo", "CREATE INDEX IF NOT EXISTS idx_photo_tag_photo ON photo_tag(photo_id)")
        _create_index_if_not_exists(conn, "idx_photo_tag_tag", "CREATE INDEX IF NOT EXISTS idx_photo_tag_tag ON photo_tag(tag_id)")
        conn.commit()


def _create_index_if_not_exists(conn, index_name: str, ddl: str):
    """Create an index, silently ignoring if already exists."""
    try:
        conn.execute(text(ddl))
    except Exception as e:
        logger.debug(f"Index {index_name} may already exist: {e}")


def get_session():
    with Session(engine) as session:
        yield session


def vacuum_database():
    """VACUUM the database to reclaim space. Call periodically."""
    try:
        with engine.connect() as conn:
            conn.execute(text("VACUUM"))
            conn.execute(text("PRAGMA optimize"))
        logger.info("Database VACUUM completed")
        return True
    except Exception as e:
        logger.error(f"Database VACUUM failed: {e}")
        return False


def check_database_integrity() -> list[str]:
    """Run integrity check and return list of issues (empty = clean)."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA integrity_check"))
            issues = [row[0] for row in result if row[0] != "ok"]
            return issues
    except Exception as e:
        return [f"Integrity check failed: {e}"]
