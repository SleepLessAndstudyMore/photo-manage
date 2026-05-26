from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/faces", tags=["faces"])


# 字面路径必须在参数化路径之前注册
@router.get("/clusters")
async def list_clusters():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/clusters/merge")
async def merge_clusters():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/detect")
async def detect_faces():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/clusters/{cluster_id}")
async def get_cluster(cluster_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/clusters/{cluster_id}/photos")
async def get_cluster_photos(cluster_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/clusters/{cluster_id}")
async def update_cluster(cluster_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/clusters/{cluster_id}/split")
async def split_cluster(cluster_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
