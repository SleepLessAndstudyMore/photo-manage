from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])


@router.get("")
async def list_photos(page: int = 1, page_size: int = 50):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{photo_id}")
async def get_photo(photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{photo_id}/exif")
async def get_photo_exif(photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{photo_id}")
async def update_photo(photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/search")
async def search_photos():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/duplicates")
async def get_duplicates():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/{photo_id}/stream")
async def stream_video(photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
