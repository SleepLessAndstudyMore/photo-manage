from typing import TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo import Photo
    from .album import Album


class PhotoAlbum(SQLModel, table=True):
    __tablename__ = "photo_album"

    photo_id: int = Field(primary_key=True, foreign_key="photo.id")
    album_id: int = Field(primary_key=True, foreign_key="album.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photo: "Photo" = Relationship(back_populates="albums")
    album: "Album" = Relationship(back_populates="photos")
