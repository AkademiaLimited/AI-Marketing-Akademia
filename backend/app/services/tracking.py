import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import MarketingActivity, WorkflowRun


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_workflow_run(
    db: AsyncSession,
    workflow_type: str,
    lead_id: str = "",
) -> WorkflowRun:
    run = WorkflowRun(
        id=str(uuid.uuid4()),
        workflow_type=workflow_type,
        status="running",
        lead_id=lead_id,
        started_at=utc_now(),
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def record_activity(
    db: AsyncSession,
    workflow_run_id: str,
    activity_type: str,
    *,
    lead_id: str = "",
    email_id: str = "",
    channel: str = "",
    source_url: str = "",
    status: str = "completed",
    details: str = "",
    error: str = "",
) -> MarketingActivity:
    activity = MarketingActivity(
        id=str(uuid.uuid4()),
        workflow_run_id=workflow_run_id,
        lead_id=lead_id,
        email_id=email_id,
        activity_type=activity_type,
        channel=channel,
        source_url=source_url,
        status=status,
        details=details,
        error=error,
        created_at=utc_now(),
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity


async def finish_workflow_run(
    db: AsyncSession,
    run: WorkflowRun,
    *,
    status: str,
    error: str = "",
) -> WorkflowRun:
    run.status = status
    run.error = error
    run.finished_at = utc_now()
    await db.commit()
    await db.refresh(run)
    return run