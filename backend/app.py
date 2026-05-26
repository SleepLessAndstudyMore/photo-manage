import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from backend.database import init_db
from backend.routers import (
    libraries_router,
    photos_router,
    tags_router,
    albums_router,
    faces_router,
    system_router,
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except Exception:
                dead.append(connection)
        for conn in dead:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


ws_manager = ConnectionManager()


def _broadcast_sync(message: dict):
    """Thread-safe WebSocket broadcast, called from sync task threads."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(message), loop)
    except RuntimeError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    from backend.tasks.task_manager import task_manager
    task_manager.set_ws_broadcast(_broadcast_sync)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="PhotoManager",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(libraries_router)
    app.include_router(photos_router)
    app.include_router(tags_router)
    app.include_router(albums_router)
    app.include_router(faces_router)
    app.include_router(system_router)

    # WebSocket endpoint for real-time progress
    @app.websocket("/api/v1/ws/notifications")
    async def websocket_notifications(websocket: WebSocket):
        await ws_manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
        except Exception:
            ws_manager.disconnect(websocket)

    # Mount thumbnails static directory (before frontend mount in main.py)
    settings.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/thumbnails",
        StaticFiles(directory=str(settings.THUMBNAIL_DIR)),
        name="thumbnails",
    )

    return app
