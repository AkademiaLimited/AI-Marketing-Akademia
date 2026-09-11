from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.email import Email
from app.schemas.email import EmailCreate, EmailOut

router = APIRouter()


@router.get("/", response_model=list[EmailOut])
async def list_emails(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Email))
    return result.scalars().all()


@router.get("/{email_id}", response_model=EmailOut)
async def get_email(email_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Email).where(Email.id == email_id))
    email = result.scalar_one_or_none()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email


@router.post("/", response_model=EmailOut, status_code=201)
async def create_email(payload: EmailCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    email = Email(**payload.model_dump())
    db.add(email)
    await db.commit()
    await db.refresh(email)
    return email
