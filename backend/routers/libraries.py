import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.library_source import LibrarySource
from backend.models.photo import Photo
from backend.models.photo_tag import PhotoTag
from backend.models.photo_album import PhotoAlbum
from backend.models.photo_face import PhotoFace
from backend.models.photo_embedding import PhotoEmbedding
from backend.models.face_cluster import FaceCluster
from backend.schemas.library import (
    LibraryCreate, LibraryResponse, LibraryListResponse, ScanTriggerResponse,
)
from backend.services.scanner import Scanner
from backend.tasks.task_manager import task_manager, TaskType

router = APIRouter(prefix="/api/v1/libraries", tags=["libraries"])


def _get_scanner() -> Scanner:
    from backend.database import Session as _Session, engine
    return Scanner(lambda: _Session(engine))


@router.get("", response_model=LibraryListResponse)
async def list_libraries(session: Session = Depends(get_session)):
    libraries = session.exec(select(LibrarySource).order_by(LibrarySource.created_at.desc())).all()
    return LibraryListResponse(
        items=[LibraryResponse.model_validate(lib) for lib in libraries]
    )


@router.post("", response_model=LibraryResponse, status_code=201)
async def add_library(
    body: LibraryCreate,
    session: Session = Depends(get_session),
):
    path = os.path.abspath(body.path)
    if not os.path.isdir(path):
        raise HTTPException(status_code=400, detail=f"目录不存在: {path}")

    existing = session.exec(
        select(LibrarySource).where(LibrarySource.path == path)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="该目录已添加为图库源")

    library = LibrarySource(name=body.name.strip(), path=path, type="local")
    session.add(library)
    session.commit()
    session.refresh(library)

    scanner = _get_scanner()
    task_id = task_manager.create_and_run(
        TaskType.SCAN,
        scanner.scan_library,
        args=(library.id, True),
        library_id=library.id,
    )

    return LibraryResponse.model_validate(library)


@router.delete("/{library_id}", status_code=204)
async def delete_library(
    library_id: int,
    session: Session = Depends(get_session),
):
    library = session.get(LibrarySource, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="图库源不存在")

    # Delete associated photos and their thumbnails
    photos = session.exec(
        select(Photo).where(Photo.library_source_id == library_id)
    ).all()
    for photo in photos:
        # Delete related records first (no cascade configured)
        for tag_link in session.exec(select(PhotoTag).where(PhotoTag.photo_id == photo.id)).all():
            session.delete(tag_link)
        for album_link in session.exec(select(PhotoAlbum).where(PhotoAlbum.photo_id == photo.id)).all():
            session.delete(album_link)
        for face in session.exec(select(PhotoFace).where(PhotoFace.photo_id == photo.id)).all():
            # Delete face thumbnails
            if face.thumbnail_path:
                fpath = Path("thumbnails") / face.thumbnail_path
                if fpath.exists():
                    try:
                        fpath.unlink()
                    except OSError:
                        pass
            session.delete(face)
        for emb in session.exec(select(PhotoEmbedding).where(PhotoEmbedding.photo_id == photo.id)).all():
            session.delete(emb)

        # Delete thumbnail/preview files
        for attr in ("thumbnail_path", "preview_path"):
            fname = getattr(photo, attr, None)
            if fname:
                fpath = Path("thumbnails") / fname
                if fpath.exists():
                    try:
                        fpath.unlink()
                    except OSError:
                        pass
        session.delete(photo)

    session.delete(library)

    # Clean up orphaned FaceClusters (no remaining faces after photo deletion)
    orphan_clusters = session.exec(
        select(FaceCluster).where(
            ~FaceCluster.id.in_(
                select(PhotoFace.face_cluster_id).where(
                    PhotoFace.face_cluster_id.is_not(None)
                ).distinct()
            )
        )
    ).all()
    for cluster in orphan_clusters:
        session.delete(cluster)

    session.commit()
    return None


@router.post("/{library_id}/scan", response_model=ScanTriggerResponse)
async def trigger_scan(
    library_id: int,
    session: Session = Depends(get_session),
):
    library = session.get(LibrarySource, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="图库源不存在")
    if library.scan_status == "scanning":
        raise HTTPException(status_code=409, detail="该图库源正在扫描中")

    scanner = _get_scanner()
    task_id = task_manager.create_and_run(
        TaskType.SCAN,
        scanner.scan_library,
        args=(library_id, False),
        library_id=library_id,
    )
    return ScanTriggerResponse(task_id=task_id, status="running", message="扫描已启动")


@router.post("/{library_id}/check-consistency", response_model=ScanTriggerResponse)
async def check_consistency(
    library_id: int,
    session: Session = Depends(get_session),
):
    library = session.get(LibrarySource, library_id)
    if not library:
        raise HTTPException(status_code=404, detail="图库源不存在")

    scanner = _get_scanner()
    task_id = task_manager.create_and_run(
        TaskType.CONSISTENCY,
        scanner.check_consistency,
        args=(library_id,),
        library_id=library_id,
    )
    return ScanTriggerResponse(task_id=task_id, status="running", message="一致性校验已启动")
