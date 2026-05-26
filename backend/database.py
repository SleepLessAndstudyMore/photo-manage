from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

from config.settings import settings
from backend.models import *  # noqa: F401 F403 — ensure all models register on metadata

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """Create all tables and enable WAL mode."""
    SQLModel.metadata.create_all(engine)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.commit()


def get_session():
    with Session(engine) as session:
        yield session
