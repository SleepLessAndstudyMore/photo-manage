from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo import Photo


class PhotoEmbedding(SQLModel, table=True):
    __tablename__ = "photo_embedding"

    photo_id: int = Field(primary_key=True, foreign_key="photo.id")
    embedding_blob: bytes = Field(nullable=False)
    embedding_model: str = Field(default="clip-vit-b-32")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photo: Optional["Photo"] = Relationship(back_populates="embedding")
