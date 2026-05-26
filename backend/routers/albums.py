from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.album import Album
from backend.models.photo_album import PhotoAlbum
from backend.models.photo import Photo
from backend.schemas.photo import PhotoResponse

router = APIRouter(prefix="/api/v1/albums", tags=["albums"])


class AlbumResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    cover_photo_id: int | None = None
    photo_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    cover_thumbnail: str | None = None

    model_config = {"from_attributes": True}


class AlbumListResponse(BaseModel):
    items: list[AlbumResponse]
    total: int


class AlbumCreate(BaseModel):
    name: str
    description: str | None = None


class AlbumUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cover_photo_id: int | None = None


class AlbumPhotoIds(BaseModel):
    photo_ids: list[int]


@router.get("", response_model=AlbumListResponse)
async def list_albums(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    base = select(Album).order_by(Album.updated_at.desc())
    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    albums = session.exec(base.offset((page - 1) * page_size).limit(page_size)).all()

    items = []
    for album in albums:
        resp = AlbumResponse.model_validate(album)
        # Fetch cover thumbnail
        if album.cover_photo_id:
            cover = session.get(Photo, album.cover_photo_id)
            if cover:
                resp.cover_thumbnail = cover.thumbnail_path
        items.append(resp)

    return AlbumListResponse(items=items, total=total)


@router.post("", response_model=AlbumResponse, status_code=201)
async def create_album(
    body: AlbumCreate,
    session: Session = Depends(get_session),
):
    album = Album(name=body.name.strip(), description=body.description)
    session.add(album)
    session.commit()
    session.refresh(album)
    return AlbumResponse.model_validate(album)


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(album_id: int, session: Session = Depends(get_session)):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")
    resp = AlbumResponse.model_validate(album)
    if album.cover_photo_id:
        cover = session.get(Photo, album.cover_photo_id)
        if cover:
            resp.cover_thumbnail = cover.thumbnail_path
    return resp


@router.put("/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    body: AlbumUpdate,
    session: Session = Depends(get_session),
):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    if body.name is not None:
        album.name = body.name.strip()
    if body.description is not None:
        album.description = body.description
    if body.cover_photo_id is not None:
        album.cover_photo_id = body.cover_photo_id
    album.updated_at = datetime.utcnow()

    session.add(album)
    session.commit()
    session.refresh(album)
    return AlbumResponse.model_validate(album)


@router.delete("/{album_id}", status_code=204)
async def delete_album(
    album_id: int,
    session: Session = Depends(get_session),
):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    # Remove all photo-album associations
    pas = session.exec(
        select(PhotoAlbum).where(PhotoAlbum.album_id == album_id)
    ).all()
    for pa in pas:
        session.delete(pa)

    session.delete(album)
    session.commit()
    return None


@router.get("/{album_id}/photos", response_model=dict)
async def get_album_photos(
    album_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    base = (
        select(Photo)
        .join(PhotoAlbum)
        .where(PhotoAlbum.album_id == album_id, Photo.file_missing == False)  # noqa: E712
        .order_by(PhotoAlbum.created_at.desc())
    )
    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    photos = session.exec(base.offset((page - 1) * page_size).limit(page_size)).all()

    return {
        "album": AlbumResponse.model_validate(album),
        "items": [PhotoResponse.model_validate(p) for p in photos],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/{album_id}/photos", response_model=dict)
async def add_photos_to_album(
    album_id: int,
    body: AlbumPhotoIds,
    session: Session = Depends(get_session),
):
    album = session.get(Album, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="相册不存在")

    added = 0
    for pid in body.photo_ids:
        existing = session.exec(
            select(PhotoAlbum).where(
                PhotoAlbum.photo_id == pid,
                PhotoAlbum.album_id == album_id,
            )
        ).first()
        if not existing:
            pa = PhotoAlbum(photo_id=pid, album_id=album_id)
            session.add(pa)
            added += 1

    # Update photo count
    album.photo_count = session.exec(
        select(func.count(PhotoAlbum.photo_id))
        .where(PhotoAlbum.album_id == album_id)
    ).one()
    album.updated_at = datetime.utcnow()
    session.add(album)
    session.commit()

    return {"message": f"已添加 {added} 张照片", "added": added}


@router.delete("/{album_id}/photos/{photo_id}", status_code=204)
async def remove_photo_from_album(
    album_id: int,
    photo_id: int,
    session: Session = Depends(get_session),
):
    pa = session.exec(
        select(PhotoAlbum).where(
            PhotoAlbum.photo_id == photo_id,
            PhotoAlbum.album_id == album_id,
        )
    ).first()
    if not pa:
        raise HTTPException(status_code=404, detail="相册中无此照片")

    session.delete(pa)

    # Update photo count
    album = session.get(Album, album_id)
    if album:
        album.photo_count = session.exec(
            select(func.count(PhotoAlbum.photo_id))
            .where(PhotoAlbum.album_id == album_id)
        ).one()
        album.updated_at = datetime.utcnow()
        session.add(album)

    session.commit()
    return None
