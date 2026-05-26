import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    SCAN = "scan"
    THUMBNAIL = "thumbnail"
    CONSISTENCY = "consistency"


@dataclass
class TaskInfo:
    id: str
    type: str
    status: str = TaskStatus.PENDING
    progress: float = 0.0
    message: str = ""
    library_id: int | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    _cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)

    def cancel(self):
        self._cancel_event.set()
        self.status = TaskStatus.CANCELLED
        self.updated_at = time.time()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "library_id": self.library_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskManager:
    def __init__(self):
        self._tasks: dict[str, TaskInfo] = {}
        self._lock = threading.Lock()
        self._ws_broadcast: Callable | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_ws_broadcast(self, broadcast_fn: Callable):
        self._ws_broadcast = broadcast_fn

    def create_and_run(
        self,
        task_type: str,
        target: Callable,
        args: tuple = (),
        library_id: int | None = None,
    ) -> str:
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        task_info = TaskInfo(id=task_id, type=task_type, library_id=library_id)
        with self._lock:
            self._tasks[task_id] = task_info

        task_info.status = TaskStatus.RUNNING
        task_info.updated_at = time.time()
        self._broadcast(task_info)

        def _runner():
            try:
                target(task_info, *args)
                if not task_info.is_cancelled:
                    task_info.status = TaskStatus.COMPLETED
                    task_info.progress = 1.0
                    task_info.message = "完成"
            except Exception as e:
                logger.exception(f"Task {task_id} failed: {e}")
                task_info.status = TaskStatus.FAILED
                task_info.message = str(e)
            task_info.updated_at = time.time()
            self._broadcast(task_info)

        thread = threading.Thread(target=_runner, daemon=True, name=f"task-{task_id}")
        thread.start()
        return task_id

    def update_progress(self, task_id: str, progress: float, message: str = ""):
        with self._lock:
            task_info = self._tasks.get(task_id)
        if task_info:
            task_info.progress = min(progress, 1.0)
            task_info.message = message
            task_info.updated_at = time.time()
            self._broadcast(task_info)

    def get_task(self, task_id: str) -> TaskInfo | None:
        with self._lock:
            return self._tasks.get(task_id)

    def list_tasks(self) -> list[TaskInfo]:
        with self._lock:
            return list(self._tasks.values())

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            task_info = self._tasks.get(task_id)
        if task_info and task_info.status in (TaskStatus.RUNNING, TaskStatus.PENDING):
            task_info.cancel()
            self._broadcast(task_info)
            return True
        return False

    def _broadcast(self, task_info: TaskInfo):
        if self._ws_broadcast:
            try:
                self._ws_broadcast({
                    "type": f"{task_info.type}_progress",
                    "data": {
                        "task_id": task_info.id,
                        "library_id": task_info.library_id,
                        "progress": task_info.progress,
                        "message": task_info.message,
                        "status": task_info.status,
                    }
                })
            except Exception:
                pass


task_manager = TaskManager()
