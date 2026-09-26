from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.routers.auth import get_current_admin
from app.models.lead import Lead
from app.models.product import Product
from app.models.email import Email
from app.models.campaign import Campaign
from app.models.workflow import MarketingActivity, WorkflowRun
from app.services.brand_service import get_active_brand

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


@router.get("/progress")
async def dashboard_progress(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Return system-wide progress metrics for dashboard visualizations.

    Includes:
      - marketing_pipeline: product counts by marketing_status
      - lead_funnel: lead counts by status
      - email_pipeline: email counts by status
      - campaign_status: campaign counts by status
      - workflow_runs: workflow run counts by status
      - active_brand: name of the admin's active brand profile (if any)
      - recent_activity: latest 10 marketing activities
    """
    # Marketing pipeline: products by marketing_status
    mkt_result = await db.execute(
        select(Product.marketing_status, func.count(Product.id)).group_by(Product.marketing_status)
    )
    marketing_counts = {status: count for status, count in mkt_result.all()}

    # Lead funnel: leads by status
    lead_result = await db.execute(
        select(Lead.status, func.count(Lead.id)).group_by(Lead.status)
    )
    lead_counts = {status: count for status, count in lead_result.all()}

    # Email pipeline: emails by status
    email_result = await db.execute(
        select(Email.status, func.count(Email.id)).group_by(Email.status)
    )
    email_counts = {status: count for status, count in email_result.all()}

    # Campaign status
    camp_result = await db.execute(
        select(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status)
    )
    campaign_counts = {status: count for status, count in camp_result.all()}

    # Workflow runs by status
    wf_result = await db.execute(
        select(WorkflowRun.status, func.count(WorkflowRun.id)).group_by(WorkflowRun.status)
    )
    workflow_counts = {status: count for status, count in wf_result.all()}

    # Active brand name
    active_brand = await get_active_brand(_admin.id, db)
    brand_name = active_brand.name if active_brand else None

    # Recent activity (last 10)
    act_result = await db.execute(
        select(MarketingActivity)
        .order_by(MarketingActivity.created_at.desc())
        .limit(10)
    )
    recent = [
        {
            "id": a.id,
            "activity_type": a.activity_type,
            "status": a.status,
            "details": a.details,
            "created_at": a.created_at,
        }
        for a in act_result.scalars().all()
    ]

    return {
        "marketing_pipeline": marketing_counts,
        "lead_funnel": lead_counts,
        "email_pipeline": email_counts,
        "campaign_status": campaign_counts,
        "workflow_runs": workflow_counts,
        "active_brand": brand_name,
        "recent_activity": recent,
    }
