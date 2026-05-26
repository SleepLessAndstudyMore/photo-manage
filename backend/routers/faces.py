import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.photo import Photo
from backend.models.photo_face import PhotoFace
from backend.models.face_cluster import FaceCluster
from backend.schemas.face import (
    FaceClusterResponse, FaceClusterDetailResponse, FaceClusterListResponse,
    PhotoFaceBrief, MergeClusterRequest, UpdateClusterRequest,
)
from backend.tasks.task_manager import task_manager, TaskType
from backend.services.face_service import get_face_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/faces", tags=["faces"])


@router.get("/clusters", response_model=FaceClusterListResponse)
async def list_clusters(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    base = select(FaceCluster).order_by(FaceCluster.face_count.desc())
    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    clusters = session.exec(
        base.offset((page - 1) * page_size).limit(page_size)
    ).all()

    items = []
    for c in clusters:
        resp = FaceClusterResponse.model_validate(c)
        # Fetch representative face thumbnail
        if c.representative_face_id:
            rep_face = session.get(PhotoFace, c.representative_face_id)
            if rep_face and rep_face.thumbnail_path:
                resp.cover_thumbnail = rep_face.thumbnail_path
        items.append(resp)

    return FaceClusterListResponse(items=items, total=total)


@router.get("/clusters/{cluster_id}", response_model=FaceClusterDetailResponse)
async def get_cluster(
    cluster_id: int,
    session: Session = Depends(get_session),
):
    cluster = session.get(FaceCluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="人脸簇不存在")

    resp = FaceClusterDetailResponse.model_validate(cluster)
    if cluster.representative_face_id:
        rep_face = session.get(PhotoFace, cluster.representative_face_id)
        if rep_face and rep_face.thumbnail_path:
            resp.cover_thumbnail = rep_face.thumbnail_path

    faces = session.exec(
        select(PhotoFace).where(PhotoFace.face_cluster_id == cluster_id)
    ).all()
    resp.faces = [PhotoFaceBrief.model_validate(f) for f in faces]
    return resp


@router.get("/clusters/{cluster_id}/photos")
async def get_cluster_photos(
    cluster_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    cluster = session.get(FaceCluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="人脸簇不存在")

    # Get distinct photo IDs for this cluster
    photo_ids_q = (
        select(PhotoFace.photo_id)
        .where(PhotoFace.face_cluster_id == cluster_id)
        .distinct()
    )
    all_ids = list(session.exec(photo_ids_q).all())
    total = len(all_ids)

    # Paginate IDs
    start = (page - 1) * page_size
    page_ids = all_ids[start : start + page_size]
    if not page_ids:
        return {"items": [], "total": total, "page": page, "page_size": page_size}

    photos = session.exec(
        select(Photo)
        .where(Photo.id.in_(page_ids), Photo.file_missing == False)  # noqa: E712
        .order_by(Photo.date_taken.desc())
    ).all()

    from backend.schemas.photo import PhotoResponse
    return {
        "items": [PhotoResponse.model_validate(p) for p in photos],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/clusters/{cluster_id}", response_model=FaceClusterResponse)
async def update_cluster(
    cluster_id: int,
    body: UpdateClusterRequest,
    session: Session = Depends(get_session),
):
    cluster = session.get(FaceCluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="人脸簇不存在")

    cluster.name = body.name
    session.add(cluster)
    session.commit()
    session.refresh(cluster)

    resp = FaceClusterResponse.model_validate(cluster)
    if cluster.representative_face_id:
        rep_face = session.get(PhotoFace, cluster.representative_face_id)
        if rep_face and rep_face.thumbnail_path:
            resp.cover_thumbnail = rep_face.thumbnail_path
    return resp


@router.post("/clusters/merge")
async def merge_clusters(
    body: MergeClusterRequest,
    session: Session = Depends(get_session),
):
    if len(body.cluster_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要合并两个簇")

    clusters = []
    for cid in body.cluster_ids:
        c = session.get(FaceCluster, cid)
        if not c:
            raise HTTPException(status_code=404, detail=f"人脸簇 {cid} 不存在")
        clusters.append(c)

    # Keep the first cluster as target, merge others into it
    target = clusters[0]
    merged_face_count = target.face_count

    for source in clusters[1:]:
        # Reassign all faces from source to target
        faces = session.exec(
            select(PhotoFace).where(PhotoFace.face_cluster_id == source.id)
        ).all()
        for f in faces:
            f.face_cluster_id = target.id
            session.add(f)
        merged_face_count += source.face_count
        session.delete(source)

    target.face_count = merged_face_count
    session.add(target)
    session.commit()
    session.refresh(target)

    resp = FaceClusterResponse.model_validate(target)
    if target.representative_face_id:
        rep_face = session.get(PhotoFace, target.representative_face_id)
        if rep_face and rep_face.thumbnail_path:
            resp.cover_thumbnail = rep_face.thumbnail_path
    return resp


@router.post("/clusters/{cluster_id}/split")
async def split_cluster(
    cluster_id: int,
    body: dict,
    session: Session = Depends(get_session),
):
    """Split a cluster: move specified face_ids into a new cluster."""
    face_ids = body.get("face_ids", [])
    if not face_ids:
        raise HTTPException(status_code=400, detail="请指定要拆分的人脸 ID")

    cluster = session.get(FaceCluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="人脸簇不存在")

    # Verify faces belong to this cluster
    faces = session.exec(
        select(PhotoFace).where(
            PhotoFace.id.in_(face_ids),
            PhotoFace.face_cluster_id == cluster_id,
        )
    ).all()

    if not faces:
        raise HTTPException(status_code=400, detail="未找到指定的人脸")

    # Create new cluster
    new_cluster = FaceCluster(face_count=len(faces))
    session.add(new_cluster)
    session.flush()

    # Move faces
    for f in faces:
        f.face_cluster_id = new_cluster.id
        session.add(f)

    new_cluster.representative_face_id = faces[0].id
    session.add(new_cluster)

    # Update face counts
    remaining = session.exec(
        select(func.count(PhotoFace.id))
        .where(PhotoFace.face_cluster_id == cluster_id)
    ).one()
    cluster.face_count = remaining
    session.add(cluster)

    session.commit()
    session.refresh(new_cluster)

    return {"message": "拆分成功", "new_cluster_id": new_cluster.id}


@router.post("/detect")
async def detect_faces():
    """Trigger face detection for all photos without faces."""
    from backend.database import engine as _engine
    from sqlmodel import Session as _Session

    db_session_factory = lambda: _Session(_engine)
    from backend.services.face_service import FaceService

    svc = FaceService(db_session_factory)
    task_id = task_manager.create_and_run(
        TaskType.FACE_DETECT,
        svc.detect_all_faces,
        args=(),
    )
    return {"message": "人脸检测任务已启动", "task_id": task_id}


@router.post("/cluster")
async def cluster_faces():
    """Trigger face clustering for all unclustered faces."""
    from backend.database import engine as _engine
    from sqlmodel import Session as _Session

    db_session_factory = lambda: _Session(_engine)
    from backend.services.face_service import FaceService

    svc = FaceService(db_session_factory)
    task_id = task_manager.create_and_run(
        TaskType.FACE_CLUSTER,
        svc.run_clustering,
        args=(),
    )
    return {"message": "人脸聚类任务已启动", "task_id": task_id}
