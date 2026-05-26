from .libraries import router as libraries_router
from .photos import router as photos_router
from .tags import router as tags_router
from .albums import router as albums_router
from .faces import router as faces_router
from .system import router as system_router

__all__ = [
    "libraries_router",
    "photos_router",
    "tags_router",
    "albums_router",
    "faces_router",
    "system_router",
]
