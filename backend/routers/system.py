import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.photo import Photo
from backend.models.library_source import LibrarySource
from backend.tasks.task_manager import task_manager, TaskStatus
from backend.schemas.system import (
    SystemStatusResponse, TaskResponse, TaskListResponse,
    SystemConfigResponse, SystemConfigUpdate,
)
from config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["system"])

CONFIG_PATH = Path("data/config.json")


def _load_config() -> dict:
    try:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _save_config(config: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def _get_dir_size_mb(dir_path: Path) -> float:
    if not dir_path.exists():
        return 0.0
    total = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for f in filenames:
            try:
                total += (Path(dirpath) / f).stat().st_size
            except OSError:
                pass
    return total / (1024 * 1024)


@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(session: Session = Depends(get_session)):
    total_photos = session.exec(
        select(func.count(Photo.id)).where(Photo.file_missing == False)  # noqa: E712
    ).one()
    total_libraries = session.exec(
        select(func.count(LibrarySource.id))
    ).one()

    db_path = settings.BASE_DIR / "data" / "photo_manager.db"
    db_size_mb = (db_path.stat().st_size / (1024 * 1024)) if db_path.exists() else 0.0

    thumbnail_size_mb = _get_dir_size_mb(settings.THUMBNAIL_DIR)

    is_scanning = any(
        t.type == "scan" and t.status == TaskStatus.RUNNING
        for t in task_manager.list_tasks()
    )
    active_tasks = sum(
        1 for t in task_manager.list_tasks()
        if t.status == TaskStatus.RUNNING
    )

    return SystemStatusResponse(
        total_photos=total_photos,
        total_libraries=total_libraries,
        db_size_mb=round(db_size_mb, 2),
        thumbnail_size_mb=round(thumbnail_size_mb, 2),
        is_scanning=is_scanning,
        active_tasks=active_tasks,
    )


@router.get("/system/config", response_model=SystemConfigResponse)
async def get_system_config():
    config = _load_config()
    return SystemConfigResponse(
        scan_interval=config.get("scan_interval", settings.SCAN_INTERVAL),
        page_size_default=config.get("page_size_default", settings.PAGE_SIZE_DEFAULT),
        thumbnail_quality=config.get("thumbnail_quality", settings.THUMBNAIL_QUALITY),
        watchdog_enabled=config.get("watchdog_enabled", False),
    )


@router.put("/system/config", response_model=SystemConfigResponse)
async def update_system_config(body: SystemConfigUpdate):
    config = _load_config()
    if body.scan_interval is not None:
        config["scan_interval"] = body.scan_interval
    if body.page_size_default is not None:
        config["page_size_default"] = body.page_size_default
    if body.thumbnail_quality is not None:
        config["thumbnail_quality"] = body.thumbnail_quality
    if body.watchdog_enabled is not None:
        config["watchdog_enabled"] = body.watchdog_enabled
    _save_config(config)
    return SystemConfigResponse(
        scan_interval=config.get("scan_interval", settings.SCAN_INTERVAL),
        page_size_default=config.get("page_size_default", settings.PAGE_SIZE_DEFAULT),
        thumbnail_quality=config.get("thumbnail_quality", settings.THUMBNAIL_QUALITY),
        watchdog_enabled=config.get("watchdog_enabled", False),
    )


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks():
    tasks = task_manager.list_tasks()
    tasks_sorted = sorted(tasks, key=lambda t: t.created_at, reverse=True)
    return TaskListResponse(
        items=[TaskResponse(**t.to_dict()) for t in tasks_sorted]
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse(**task.to_dict())


@router.post("/tasks/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: str):
    ok = task_manager.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="任务不存在或已完成")
    task = task_manager.get_task(task_id)
    return TaskResponse(**task.to_dict())
