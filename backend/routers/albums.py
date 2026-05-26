from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/albums", tags=["albums"])


@router.get("")
async def list_albums():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("")
async def create_album():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/{album_id}")
async def update_album(album_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{album_id}")
async def delete_album(album_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{album_id}/photos")
async def add_photos_to_album(album_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{album_id}/photos/{photo_id}")
async def remove_photo_from_album(album_id: int, photo_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
