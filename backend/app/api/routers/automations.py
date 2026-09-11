from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.automation import Automation
from app.schemas.automation import AutomationCreate, AutomationOut

router = APIRouter()


@router.get("/", response_model=list[AutomationOut])
async def list_automations(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Automation))
    return result.scalars().all()


@router.get("/{automation_id}", response_model=AutomationOut)
async def get_automation(automation_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Automation).where(Automation.id == automation_id))
    automation = result.scalar_one_or_none()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation


@router.post("/", response_model=AutomationOut, status_code=201)
async def create_automation(payload: AutomationCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    automation = Automation(**payload.model_dump())
    db.add(automation)
    await db.commit()
    await db.refresh(automation)
    return automation


@router.patch("/{automation_id}", response_model=AutomationOut)
async def update_automation(automation_id: str, payload: dict, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Automation).where(Automation.id == automation_id))
    automation = result.scalar_one_or_none()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    for key, value in payload.items():
        if hasattr(automation, key):
            setattr(automation, key, value)
    await db.commit()
    await db.refresh(automation)
    return automation
