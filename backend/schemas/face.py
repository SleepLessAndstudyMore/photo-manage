from datetime import datetime

from pydantic import BaseModel, Field


class PhotoFaceBrief(BaseModel):
    id: int
    photo_id: int
    face_cluster_id: int | None = None
    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int
    confidence: float
    thumbnail_path: str | None = None

    model_config = {"from_attributes": True}


class FaceClusterResponse(BaseModel):
    id: int
    name: str | None = None
    representative_face_id: int | None = None
    face_count: int = 0
    cover_thumbnail: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class FaceClusterDetailResponse(FaceClusterResponse):
    faces: list[PhotoFaceBrief] = []


class FaceClusterListResponse(BaseModel):
    items: list[FaceClusterResponse]
    total: int


class MergeClusterRequest(BaseModel):
    cluster_ids: list[int] = Field(min_length=2)


class UpdateClusterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)
