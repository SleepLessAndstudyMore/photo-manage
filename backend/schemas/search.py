from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.photo import PhotoResponse


class SearchResultItem(PhotoResponse):
    similarity_score: float | None = None


class SearchResponse(BaseModel):
    items: list[SearchResultItem]
    total: int
    page: int
    page_size: int
