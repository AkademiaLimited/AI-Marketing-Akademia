from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadOut

router = APIRouter()


@router.get("/", response_model=list[LeadOut])
async def list_leads(db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Lead))
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    lead = Lead(**payload.model_dump())
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.patch("/{lead_id}/status", response_model=LeadOut)
async def update_lead_status(lead_id: str, status: str = Body(..., embed=True), db: AsyncSession = Depends(get_db), _admin=Depends(get_current_admin)):
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = status
    await db.commit()
    await db.refresh(lead)
    return lead
