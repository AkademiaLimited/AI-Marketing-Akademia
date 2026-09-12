from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.auth import get_current_admin
from app.core.database import get_db
from app.models.workflow import MarketingActivity, WorkflowRun
from app.schemas.workflow import MarketingActivityOut, WorkflowRunOut

router = APIRouter()


@router.get("/runs", response_model=list[WorkflowRunOut])
async def list_workflow_runs(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(select(WorkflowRun).order_by(desc(WorkflowRun.started_at)))
    return result.scalars().all()


@router.get("/activities", response_model=list[MarketingActivityOut])
async def list_marketing_activities(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(MarketingActivity).order_by(desc(MarketingActivity.created_at))
    )
    return result.scalars().all()