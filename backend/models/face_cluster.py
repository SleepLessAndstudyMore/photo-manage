from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo_face import PhotoFace


class FaceCluster(SQLModel, table=True):
    __tablename__ = "face_cluster"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = Field(default=None)
    representative_face_id: Optional[int] = Field(default=None, foreign_key="photo_face.id")
    face_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    faces: list["PhotoFace"] = Relationship(
        back_populates="face_cluster",
        sa_relationship_kwargs={"foreign_keys": "[PhotoFace.face_cluster_id]"},
    )
