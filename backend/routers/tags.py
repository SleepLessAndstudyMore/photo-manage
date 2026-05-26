from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["tags"])


@router.get("/tags")
async def list_tags():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/tags/{tag_id}/photos")
async def get_tag_photos(tag_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/photos/{photo_id}/tags")
async def add_tag_to_photo(photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/photos/{photo_id}/tags/{tag_id}")
async def remove_tag_from_photo(photo_id: int, tag_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
