from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo import Photo
    from .tag import Tag


class PhotoTag(SQLModel, table=True):
    __tablename__ = "photo_tag"

    photo_id: int = Field(primary_key=True, foreign_key="photo.id")
    tag_id: int = Field(primary_key=True, foreign_key="tag.id")
    confidence: Optional[float] = Field(default=None)
    source: str = Field(default="auto")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photo: "Photo" = Relationship(back_populates="tags")
    tag: "Tag" = Relationship(back_populates="photos")
