from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo_album import PhotoAlbum


class Album(SQLModel, table=True):
    __tablename__ = "album"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    cover_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")
    photo_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    photos: list["PhotoAlbum"] = Relationship(back_populates="album")
