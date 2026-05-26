from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo import Photo
    from .face_cluster import FaceCluster


class PhotoFace(SQLModel, table=True):
    __tablename__ = "photo_face"

    id: Optional[int] = Field(default=None, primary_key=True)
    photo_id: int = Field(foreign_key="photo.id")
    face_cluster_id: Optional[int] = Field(default=None, foreign_key="face_cluster.id")
    bbox_x: int = Field(nullable=False)
    bbox_y: int = Field(nullable=False)
    bbox_w: int = Field(nullable=False)
    bbox_h: int = Field(nullable=False)
    face_embedding: bytes = Field(nullable=False)
    confidence: float = Field(nullable=False)
    thumbnail_path: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photo: "Photo" = Relationship(back_populates="faces")
    face_cluster: Optional["FaceCluster"] = Relationship(back_populates="faces")
