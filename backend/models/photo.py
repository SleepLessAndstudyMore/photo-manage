from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo_tag import PhotoTag
    from .photo_album import PhotoAlbum
    from .photo_face import PhotoFace
    from .photo_embedding import PhotoEmbedding


class Photo(SQLModel, table=True):
    __tablename__ = "photo"

    id: Optional[int] = Field(default=None, primary_key=True)
    library_source_id: Optional[int] = Field(default=None, foreign_key="library_source.id", index=True)
    file_path: str = Field(nullable=False, unique=True)
    file_name: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    file_hash: Optional[str] = Field(default=None, index=True)
    phash: Optional[str] = Field(default=None, index=True)
    is_video: bool = Field(default=False)
    date_taken: Optional[datetime] = Field(default=None, index=True)
    date_modified: Optional[datetime] = Field(default=None)
    thumbnail_path: Optional[str] = Field(default=None)
    thumbnail_width: Optional[int] = Field(default=None)
    thumbnail_height: Optional[int] = Field(default=None)
    preview_path: Optional[str] = Field(default=None)
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    orientation: int = Field(default=1)
    camera_make: Optional[str] = Field(default=None)
    camera_model: Optional[str] = Field(default=None, index=True)
    lens_model: Optional[str] = Field(default=None)
    f_number: Optional[float] = Field(default=None)
    exposure_time: Optional[str] = Field(default=None)
    iso: Optional[int] = Field(default=None)
    focal_length: Optional[float] = Field(default=None)
    gps_latitude: Optional[float] = Field(default=None)
    gps_longitude: Optional[float] = Field(default=None)
    file_modified_time: Optional[float] = Field(default=None)
    rating: int = Field(default=0)
    is_favorite: bool = Field(default=False)
    file_missing: bool = Field(default=False, index=True)
    duration: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    library_source: Optional["LibrarySource"] = Relationship(back_populates="photos")
    tags: list["PhotoTag"] = Relationship(back_populates="photo")
    albums: list["PhotoAlbum"] = Relationship(back_populates="photo")
    faces: list["PhotoFace"] = Relationship(back_populates="photo")
    embedding: Optional["PhotoEmbedding"] = Relationship(back_populates="photo")
