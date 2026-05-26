import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, extract
from sqlalchemy import desc as sa_desc, asc as sa_asc

from backend.database import get_session
from backend.models.photo import Photo
from backend.models.tag import Tag
from backend.models.photo_tag import PhotoTag
from backend.schemas.photo import (
    PhotoListParams, PhotoResponse, PhotoDetailResponse, PhotoExifResponse,
    PhotoUpdateRequest, PhotoListResponse, PhotoTagInfo,
    TimelineResponse, TimelineYear, TimelineMonth, TimelineDay,
    FolderItem, FolderListResponse,
)

router = APIRouter(prefix="/api/v1/photos", tags=["photos"])

SORT_COLUMNS = {
    "date_taken": Photo.date_taken,
    "file_name": Photo.file_name,
    "file_size": Photo.file_size,
}


def _build_photo_query(session: Session, params: PhotoListParams):
    query = select(Photo)

    if params.library_id is not None:
        query = query.where(Photo.library_source_id == params.library_id)
    if params.year is not None:
        query = query.where(extract("year", Photo.date_taken) == params.year)
    if params.month is not None:
        query = query.where(extract("month", Photo.date_taken) == params.month)
    if params.day is not None:
        query = query.where(extract("day", Photo.date_taken) == params.day)
    if params.folder:
        query = query.where(Photo.file_path.startswith(params.folder))

    sort_col = SORT_COLUMNS.get(params.sort_by, Photo.date_taken)
    sort_dir = sa_desc if params.sort_order == "desc" else sa_asc
    query = query.order_by(sort_dir(sort_col))

    return query


@router.get("", response_model=PhotoListResponse)
async def list_photos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    library_id: int | None = None,
    year: int | None = None,
    month: int | None = None,
    day: int | None = None,
    folder: str | None = None,
    sort_by: str = Query(default="date_taken"),
    sort_order: str = Query(default="desc"),
    session: Session = Depends(get_session),
):
    params = PhotoListParams(
        page=page, page_size=page_size, library_id=library_id,
        year=year, month=month, day=day,
        folder=folder, sort_by=sort_by, sort_order=sort_order,
    )
    base_query = _build_photo_query(session, params)
    count_query = select(func.count()).select_from(base_query.subquery())
    total = session.exec(count_query).one()

    photos = session.exec(
        base_query.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return PhotoListResponse(
        items=[PhotoResponse.model_validate(p) for p in photos],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    library_id: int | None = None,
    session: Session = Depends(get_session),
):
    base = select(Photo.date_taken)
    if library_id is not None:
        base = base.where(Photo.library_source_id == library_id)

    photos_with_dates = session.exec(
        base.where(Photo.date_taken.is_not(None)).where(
            Photo.file_missing == False  # noqa: E712
        )
    ).all()

    # Build year -> month -> day hierarchy
    year_map: dict[int, dict[int, dict[int, int]]] = {}
    for row in photos_with_dates:
        dt = row if isinstance(row, datetime) else row[0]
        if dt is None:
            continue
        y, m, d = dt.year, dt.month, dt.day
        year_map.setdefault(y, {}).setdefault(m, {}).setdefault(d, 0)
        year_map[y][m][d] += 1

    years = []
    for y in sorted(year_map, reverse=True):
        months_data = []
        y_count = 0
        for m in sorted(year_map[y], reverse=True):
            days_data = []
            m_count = 0
            for d in sorted(year_map[y][m], reverse=True):
                cnt = year_map[y][m][d]
                days_data.append(TimelineDay(day=d, count=cnt))
                m_count += cnt
            months_data.append(TimelineMonth(month=m, count=m_count, days=days_data))
            y_count += m_count
        years.append(TimelineYear(year=y, count=y_count, months=months_data))

    return TimelineResponse(years=years)


@router.get("/folders", response_model=FolderListResponse)
async def list_folders(
    library_id: int | None = None,
    session: Session = Depends(get_session),
):
    base = select(Photo)
    if library_id is not None:
        base = base.where(Photo.library_source_id == library_id)
    photos = session.exec(base.where(Photo.file_missing == False).order_by(  # noqa: E712
        Photo.file_path
    )).all()

    folder_map: dict[str, dict] = {}
    for p in photos:
        folder = os.path.dirname(p.file_path)
        if folder not in folder_map:
            folder_map[folder] = {
                "path": folder,
                "name": os.path.basename(folder),
                "photo_count": 0,
                "cover_photo": p,
            }
        folder_map[folder]["photo_count"] += 1

    items = []
    for fdata in sorted(folder_map.values(), key=lambda x: x["path"]):
        items.append(FolderItem(
            path=fdata["path"],
            name=fdata["name"],
            photo_count=fdata["photo_count"],
            cover_photo=PhotoResponse.model_validate(fdata["cover_photo"]),
        ))

    return FolderListResponse(items=items)


# ---- Static routes must come before /{photo_id} ---- #

@router.get("/gps")
async def get_gps_photos(
    bounds: str | None = None,
    library_id: int | None = None,
    session: Session = Depends(get_session),
):
    """Get photos with GPS coordinates. Optionally filter by map bounds."""
    base = select(Photo).where(
        Photo.gps_latitude.is_not(None),
        Photo.gps_longitude.is_not(None),
        Photo.file_missing == False,  # noqa: E712
    )

    if library_id is not None:
        base = base.where(Photo.library_source_id == library_id)

    if bounds:
        try:
            parts = [float(x) for x in bounds.split(",")]
            if len(parts) == 4:
                south, west, north, east = parts
                base = base.where(Photo.gps_latitude >= south)
                base = base.where(Photo.gps_latitude <= north)
                base = base.where(Photo.gps_longitude >= west)
                base = base.where(Photo.gps_longitude <= east)
        except (ValueError, TypeError):
            pass

    photos = session.exec(base.order_by(Photo.date_taken.desc())).all()
    items = []
    for p in photos:
        items.append({
            "id": p.id,
            "file_name": p.file_name,
            "latitude": p.gps_latitude,
            "longitude": p.gps_longitude,
            "thumbnail_path": p.thumbnail_path,
            "date_taken": p.date_taken.isoformat() if p.date_taken else None,
        })
    return {"items": items, "total": len(items)}


@router.post("/search", response_model=PhotoListResponse)
async def search_photos(
    body: dict,
    session: Session = Depends(get_session),
):
    from backend.services.search_engine import structured_search, hybrid_search

    mode = body.get("mode", "structured")
    page = body.get("page", 1)
    page_size = body.get("page_size", 50)

    if mode == "hybrid":
        query = body.get("query", "")
        photos, total = hybrid_search(
            session,
            query=query,
            page=page,
            page_size=page_size,
        )
    else:
        photos, total = structured_search(
            session,
            filters=body.get("filters"),
            logic=body.get("logic", "AND"),
            sort_by=body.get("sort_by", "date_taken"),
            sort_order=body.get("sort_order", "desc"),
            page=page,
            page_size=page_size,
        )

    return PhotoListResponse(
        items=[PhotoResponse.model_validate(p) for p in photos],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/duplicates")
async def get_duplicates(
    type: str = Query(default="all"),
    threshold: int = Query(default=10),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
):
    from backend.database import Session as _Session, engine
    from backend.services.duplicate_detector import DuplicateDetector

    detector = DuplicateDetector(lambda: _Session(engine))
    result = detector.find_duplicates(
        dup_type=type,
        threshold=threshold,
        page=page,
        page_size=page_size,
    )
    return result


# ---- Parameterized photo routes ---- #

@router.get("/{photo_id}", response_model=PhotoDetailResponse)
async def get_photo(photo_id: int, session: Session = Depends(get_session)):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    resp = PhotoDetailResponse.model_validate(photo)
    # Populate tags
    tags_data = []
    pts = session.exec(
        select(PhotoTag, Tag)
        .join(Tag)
        .where(PhotoTag.photo_id == photo_id)
    ).all()
    for pt, tag in pts:
        tags_data.append(PhotoTagInfo(
            id=pt.photo_id,
            tag_id=tag.id,
            tag_name=tag.name,
            tag_name_zh=tag.name_zh,
            confidence=pt.confidence,
            source=pt.source,
        ))
    resp.tags = tags_data
    return resp


@router.get("/{photo_id}/exif", response_model=PhotoExifResponse)
async def get_photo_exif(photo_id: int, session: Session = Depends(get_session)):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")
    return PhotoExifResponse(
        photo_id=photo.id,
        camera_make=photo.camera_make,
        camera_model=photo.camera_model,
        lens_model=photo.lens_model,
        f_number=photo.f_number,
        exposure_time=photo.exposure_time,
        iso=photo.iso,
        focal_length=photo.focal_length,
        gps_latitude=photo.gps_latitude,
        gps_longitude=photo.gps_longitude,
        date_taken=photo.date_taken,
        width=photo.width,
        height=photo.height,
        file_size=photo.file_size,
        orientation=photo.orientation,
    )


@router.put("/{photo_id}", response_model=PhotoDetailResponse)
async def update_photo(
    photo_id: int,
    body: PhotoUpdateRequest,
    session: Session = Depends(get_session),
):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    if body.rating is not None:
        photo.rating = body.rating
    if body.is_favorite is not None:
        photo.is_favorite = body.is_favorite
    photo.updated_at = datetime.utcnow()

    session.add(photo)
    session.commit()
    session.refresh(photo)
    return PhotoDetailResponse.model_validate(photo)


@router.get("/{photo_id}/stream")
async def stream_video(photo_id: int):
    raise HTTPException(status_code=501, detail="S2 实现")
