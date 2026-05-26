from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, func

from backend.database import get_session
from backend.models.tag import Tag
from backend.models.photo_tag import PhotoTag
from backend.models.photo import Photo
from backend.schemas.photo import PhotoResponse

router = APIRouter(prefix="/api/v1", tags=["tags"])


from datetime import datetime


class TagResponse(BaseModel):
    id: int
    name: str
    name_zh: str | None = None
    type: str
    photo_count: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    items: list[TagResponse]
    total: int


class AddTagRequest(BaseModel):
    tag_id: int | None = None
    name: str | None = None
    name_zh: str | None = None
    source: str = "manual"


class PhotoTagResponse(BaseModel):
    id: int
    tag_id: int
    tag_name: str
    tag_name_zh: str | None = None
    confidence: float | None = None
    source: str

    model_config = {"from_attributes": True}


@router.get("/tags", response_model=TagListResponse)
async def list_tags(
    type: str | None = None,
    min_confidence: float | None = None,
    sort_by: str = Query(default="photo_count"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    base = select(Tag)

    if type:
        base = base.where(Tag.type == type)

    if sort_by == "name":
        base = base.order_by(Tag.name)
    else:
        base = base.order_by(Tag.photo_count.desc())

    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    tags = session.exec(base.offset((page - 1) * page_size).limit(page_size)).all()

    return TagListResponse(
        items=[TagResponse.model_validate(t) for t in tags],
        total=total,
    )


@router.get("/tags/{tag_id}/photos", response_model=dict)
async def get_tag_photos(
    tag_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    base = (
        select(Photo)
        .join(PhotoTag)
        .where(PhotoTag.tag_id == tag_id, Photo.file_missing == False)  # noqa: E712
        .order_by(Photo.date_taken.desc())
    )
    total = session.exec(select(func.count()).select_from(base.subquery())).one()
    photos = session.exec(base.offset((page - 1) * page_size).limit(page_size)).all()

    return {
        "tag": TagResponse.model_validate(tag),
        "items": [PhotoResponse.model_validate(p) for p in photos],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/photos/{photo_id}/tags", response_model=dict)
async def add_tag_to_photo(
    photo_id: int,
    body: AddTagRequest,
    session: Session = Depends(get_session),
):
    photo = session.get(Photo, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    tag_id = body.tag_id
    if tag_id is None and body.name:
        # Create manual tag if it doesn't exist
        existing = session.exec(select(Tag).where(Tag.name == body.name)).first()
        if existing:
            tag_id = existing.id
        else:
            tag = Tag(
                name=body.name,
                name_zh=body.name_zh,
                type="manual",
                photo_count=0,
            )
            session.add(tag)
            session.flush()
            tag_id = tag.id

    if tag_id is None:
        raise HTTPException(status_code=400, detail="必须提供 tag_id 或 name")

    # Check if already tagged
    existing_pt = session.exec(
        select(PhotoTag).where(
            PhotoTag.photo_id == photo_id,
            PhotoTag.tag_id == tag_id,
        )
    ).first()
    if existing_pt:
        raise HTTPException(status_code=409, detail="该照片已有此标签")

    pt = PhotoTag(
        photo_id=photo_id,
        tag_id=tag_id,
        source=body.source,
    )
    session.add(pt)

    # Update tag count
    tag = session.get(Tag, tag_id)
    if tag:
        tag.photo_count = session.exec(
            select(func.count(PhotoTag.photo_id))
            .where(PhotoTag.tag_id == tag_id)
        ).one()
        session.add(tag)

    session.commit()
    return {"message": "标签已添加", "tag_id": tag_id}


@router.delete("/photos/{photo_id}/tags/{tag_id}", status_code=204)
async def remove_tag_from_photo(
    photo_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
):
    pt = session.exec(
        select(PhotoTag).where(
            PhotoTag.photo_id == photo_id,
            PhotoTag.tag_id == tag_id,
        )
    ).first()
    if not pt:
        raise HTTPException(status_code=404, detail="该照片无此标签")

    session.delete(pt)

    # Update tag count
    tag = session.get(Tag, tag_id)
    if tag:
        tag.photo_count = session.exec(
            select(func.count(PhotoTag.photo_id))
            .where(PhotoTag.tag_id == tag_id)
        ).one()
        session.add(tag)

    session.commit()
    return None


@router.delete("/tags/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # Remove all photo_tag associations
    pts = session.exec(
        select(PhotoTag).where(PhotoTag.tag_id == tag_id)
    ).all()
    for pt in pts:
        session.delete(pt)

    session.delete(tag)
    session.commit()
    return None


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    body: AddTagRequest,
    session: Session = Depends(get_session),
):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    if body.name_zh is not None:
        tag.name_zh = body.name_zh
    if body.name is not None:
        tag.name = body.name

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return TagResponse.model_validate(tag)
