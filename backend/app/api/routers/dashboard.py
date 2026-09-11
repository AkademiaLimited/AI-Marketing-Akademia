from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.lead import Lead

router = APIRouter()


@router.get("/summary")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    counts = {status: count for status, count in result.all()}
    return {
        "new": counts.get("new", 0),
        "contacted": counts.get("contacted", 0),
        "responded": counts.get("responded", 0),
        "needs_followup": counts.get("needs-followup", 0),
        "meetings": counts.get("meeting", 0),
        "customers": counts.get("customer", 0),
        "lost": counts.get("lost", 0),
    }
