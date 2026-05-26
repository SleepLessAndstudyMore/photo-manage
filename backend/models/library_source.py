from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .photo import Photo


class LibrarySource(SQLModel, table=True):
    __tablename__ = "library_source"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    path: str = Field(nullable=False, unique=True)
    type: str = Field(nullable=False)  # local
    scan_status: str = Field(default="idle")  # idle / scanning / completed / error
    last_scan_at: Optional[datetime] = Field(default=None)
    photo_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    photos: list["Photo"] = Relationship(back_populates="library_source")
