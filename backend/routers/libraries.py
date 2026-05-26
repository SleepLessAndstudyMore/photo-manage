from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/libraries", tags=["libraries"])


@router.get("")
async def list_libraries(page: int = 1, page_size: int = 50):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("")
async def add_library():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/{library_id}")
async def delete_library(library_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{library_id}/scan")
async def trigger_scan(library_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/{library_id}/check-consistency")
async def check_consistency(library_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
