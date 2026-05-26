from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo_tag import PhotoTag


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    name_zh: Optional[str] = Field(default=None)
    type: str = Field(nullable=False)  # auto / manual / face
    photo_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photos: list["PhotoTag"] = Relationship(back_populates="tag")
