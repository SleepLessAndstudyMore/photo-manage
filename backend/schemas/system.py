from pydantic import BaseModel, Field


class SystemStatusResponse(BaseModel):
    total_photos: int
    total_libraries: int
    db_size_mb: float
    thumbnail_size_mb: float
    is_scanning: bool
    active_tasks: int


class TaskResponse(BaseModel):
    id: str
    type: str
    status: str
    progress: float
    message: str
    library_id: int | None = None
    created_at: float
    updated_at: float


class TaskListResponse(BaseModel):
    items: list[TaskResponse]


class SystemConfigResponse(BaseModel):
    scan_interval: int = 300
    page_size_default: int = 50
    thumbnail_quality: int = 80
    watchdog_enabled: bool = False


class SystemConfigUpdate(BaseModel):
    scan_interval: int | None = Field(default=None, ge=10, le=3600)
    page_size_default: int | None = Field(default=None, ge=10, le=200)
    thumbnail_quality: int | None = Field(default=None, ge=10, le=100)
    watchdog_enabled: bool | None = None
