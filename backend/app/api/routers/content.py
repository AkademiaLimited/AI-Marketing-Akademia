from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.content import Content
from app.schemas.content import ContentCreate, ContentOut

router = APIRouter()


@router.get("/", response_model=list[ContentOut])
async def list_content(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Content))
    return result.scalars().all()


@router.get("/{content_id}", response_model=ContentOut)
async def get_content(content_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.post("/", response_model=ContentOut, status_code=201)
async def create_content(payload: ContentCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    content = Content(**payload.model_dump())
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content


@router.patch("/{content_id}", response_model=ContentOut)
async def update_content(content_id: str, payload: dict, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    for key, value in payload.items():
        if hasattr(content, key):
            setattr(content, key, value)
    await db.commit()
    await db.refresh(content)
    return content
