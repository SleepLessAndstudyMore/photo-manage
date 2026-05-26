from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.routers import (
    libraries_router,
    photos_router,
    tags_router,
    albums_router,
    faces_router,
    system_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
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

    app.include_router(libraries_router)
    app.include_router(photos_router)
    app.include_router(tags_router)
    app.include_router(albums_router)
    app.include_router(faces_router)
    app.include_router(system_router)

    return app
