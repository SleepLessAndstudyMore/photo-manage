import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.library_source import LibrarySource
from backend.models.photo import Photo
from backend.models.photo_tag import PhotoTag
from backend.models.photo_album import PhotoAlbum
from backend.models.photo_face import PhotoFace
from backend.models.photo_embedding import PhotoEmbedding
from backend.models.face_cluster import FaceCluster
from backend.models.tag import Tag
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

    # Update Tag photo_count after PhotoTag deletion
    _refresh_tag_counts(session)

    # Clean up orphaned Tags (no remaining PhotoTag associations)
    orphan_tags = session.exec(
        select(Tag).where(
            ~Tag.id.in_(
                select(PhotoTag.tag_id).where(
                    PhotoTag.tag_id.is_not(None)
                ).distinct()
            )
        )
    ).all()
    for tag in orphan_tags:
        session.delete(tag)

    # Update FaceCluster face_count after PhotoFace deletion
    _refresh_face_cluster_counts(session)

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


def _refresh_tag_counts(session: Session):
    """Recalculate Tag.photo_count from actual PhotoTag rows."""
    count_rows = session.exec(
        select(PhotoTag.tag_id, func.count(PhotoTag.photo_id))
        .group_by(PhotoTag.tag_id)
    ).all()
    tag_counts = {row[0]: row[1] for row in count_rows}
    for tag in session.exec(select(Tag)).all():
        new_count = tag_counts.get(tag.id, 0)
        if tag.photo_count != new_count:
            tag.photo_count = new_count
            session.add(tag)


def _refresh_face_cluster_counts(session: Session):
    """Recalculate FaceCluster.face_count = distinct photo count."""
    count_rows = session.exec(
        select(PhotoFace.face_cluster_id, func.count(PhotoFace.photo_id.distinct()))
        .where(PhotoFace.face_cluster_id.is_not(None))
        .group_by(PhotoFace.face_cluster_id)
    ).all()
    cluster_counts = {row[0]: row[1] for row in count_rows}
    for cluster in session.exec(select(FaceCluster)).all():
        new_count = cluster_counts.get(cluster.id, 0)
        if cluster.face_count != new_count:
            cluster.face_count = new_count
            session.add(cluster)


@router.get("/browse")
async def browse_directory(path: str = Query(default="")):
    """Browse local directory and return subdirectories.

    When path is empty, returns all available drives (Windows) or root (/).
    """
    import platform
    import string

    target = path.strip() if path else ""

    # Root level: list all drives (Windows) or root dir
    if not target:
        if platform.system() == "Windows":
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.isdir(drive):
                    drives.append({"name": f"{letter}:", "path": drive})
            return {
                "current_path": "Computer",
                "parent_path": None,
                "items": drives,
            }
        else:
            target = "/"

    target = os.path.abspath(target)
    if not os.path.isdir(target):
        raise HTTPException(status_code=400, detail=f"路径不存在: {target}")

    items = []
    try:
        for entry in os.scandir(target):
            if entry.is_dir() and not entry.name.startswith("."):
                items.append({"name": entry.name, "path": entry.path})
    except PermissionError:
        pass

    parent = str(Path(target).parent) if str(Path(target).parent) != target else None

    return {
        "current_path": target,
        "parent_path": parent,
        "items": sorted(items, key=lambda x: x["name"].lower()),
    }


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
