from datetime import datetime
from pydantic import BaseModel, Field


class PhotoListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)
    library_id: int | None = None
    year: int | None = None
    month: int | None = None
    day: int | None = None
    folder: str | None = None
    sort_by: str = Field(default="date_taken")
    sort_order: str = Field(default="desc")


class PhotoResponse(BaseModel):
    id: int
    library_source_id: int | None = None
    file_name: str
    file_path: str
    file_size: int
    is_video: bool
    date_taken: datetime | None = None
    thumbnail_path: str | None = None
    thumbnail_width: int | None = None
    thumbnail_height: int | None = None
    preview_path: str | None = None
    width: int | None = None
    height: int | None = None
    rating: int = 0
    is_favorite: bool = False
    file_missing: bool = False
    duration: float | None = None

    model_config = {"from_attributes": True}


class PhotoTagInfo(BaseModel):
    id: int
    tag_id: int
    tag_name: str
    tag_name_zh: str | None = None
    confidence: float | None = None
    source: str

    model_config = {"from_attributes": True}


class PhotoDetailResponse(PhotoResponse):
    camera_make: str | None = None
    camera_model: str | None = None
    lens_model: str | None = None
    f_number: float | None = None
    exposure_time: str | None = None
    iso: int | None = None
    focal_length: float | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    orientation: int = 1
    date_modified: datetime | None = None
    file_hash: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    file_modified_time: float | None = None
    tags: list[PhotoTagInfo] = []


class PhotoExifResponse(BaseModel):
    photo_id: int
    camera_make: str | None = None
    camera_model: str | None = None
    lens_model: str | None = None
    f_number: float | None = None
    exposure_time: str | None = None
    iso: int | None = None
    focal_length: float | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    date_taken: datetime | None = None
    width: int | None = None
    height: int | None = None
    file_size: int = 0
    orientation: int = 1

    model_config = {"from_attributes": True}


class PhotoUpdateRequest(BaseModel):
    rating: int | None = Field(default=None, ge=0, le=5)
    is_favorite: bool | None = None


class PhotoListResponse(BaseModel):
    items: list[PhotoResponse]
    total: int
    page: int
    page_size: int


class TimelineDay(BaseModel):
    day: int
    count: int


class TimelineMonth(BaseModel):
    month: int
    count: int
    days: list[TimelineDay] = []


class TimelineYear(BaseModel):
    year: int
    count: int
    months: list[TimelineMonth] = []


class TimelineResponse(BaseModel):
    years: list[TimelineYear]


class FolderItem(BaseModel):
    path: str
    name: str
    photo_count: int
    cover_photo: PhotoResponse | None = None
    preview_photos: list[PhotoResponse] = []


class FolderListResponse(BaseModel):
    items: list[FolderItem]
