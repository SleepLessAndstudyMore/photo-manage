from datetime import datetime
from pydantic import BaseModel, Field


class LibraryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    path: str = Field(..., min_length=1)


class LibraryResponse(BaseModel):
    id: int
    name: str
    path: str
    type: str
    scan_status: str
    last_scan_at: datetime | None
    photo_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LibraryListResponse(BaseModel):
    items: list[LibraryResponse]


class ScanTriggerResponse(BaseModel):
    task_id: str
    status: str
    message: str
