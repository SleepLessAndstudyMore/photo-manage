from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["system"])


@router.get("/system/status")
async def get_system_status():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/system/config")
async def get_system_config():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/system/config")
async def update_system_config():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/tasks")
async def get_tasks():
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
