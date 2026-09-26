import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.providers import get_provider
from app.core.providers.schemas import PostResponse
from app.models.generated_content import GeneratedContent
from app.models.product import Product
from app.models.publish_log import PublishLog
from app.schemas.generated_content import PublishNowRequest, SchedulePostRequest
from app.tasks.scheduled_publish import run_scheduled_publish

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/scheduled", response_model=list[dict])
async def list_scheduled_posts(
    db: AsyncSession = Depends(get_db),
):
    """List all posts scheduled for future publication."""
    result = await db.execute(
        select(GeneratedContent).where(
            GeneratedContent.status == "scheduled"
        )
    )
    posts = result.scalars().all()
    return [
        {
            "content_id": p.id,
            "platform": p.platform,
            "caption": p.caption,
            "scheduled_at": p.scheduled_at,
            "post_id": p.post_id,
        }
        for p in posts
    ]


@router.post("/schedule")
async def schedule_post(
    request: Annotated[SchedulePostRequest, Body()],
    db: AsyncSession = Depends(get_db),
):
    """Schedule a generated content item for future publishing."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == request.content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )

    if content.status != "generated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot schedule content with status '{content.status}'. Only 'generated' content can be scheduled.",
        )

    try:
        scheduled_time = datetime.fromisoformat(request.when)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO-8601.",
        )

    if scheduled_time <= datetime.now(timezone.utc).replace(tzinfo=scheduled_time.tzinfo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule a post in the past",
        )

    content.status = "scheduled"
    content.scheduled_at = request.when
    content.post_id = ""
    await db.commit()
    await db.refresh(content)

    return {
        "content_id": content.id,
        "platform": content.platform,
        "status": "scheduled",
        "scheduled_at": content.scheduled_at,
    }


@router.post("/publish")
async def publish_now(
    request: Annotated[PublishNowRequest, Body()],
    db: AsyncSession = Depends(get_db),
):
    """Publish a generated content item immediately via the provider."""
    result = await db.execute(
        select(GeneratedContent).where(GeneratedContent.id == request.content_id)
    )
    content = result.scalar_one_or_none()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )

    if content.status not in ("generated", "scheduled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish content with status '{content.status}'",
        )

    provider = get_provider(content.platform)
    provider_result = await provider.publish_post(
        {
            "caption": content.caption,
            "hashtags": content.hashtags,
            "call_to_action": content.call_to_action,
        }
    )

    result_log = await db.execute(
        select(Product).where(Product.id == content.product_id)
    )
    product = result_log.scalar_one_or_none()

    log = PublishLog(
        id=str(uuid.uuid4()),
        product_id=content.product_id,
        platform=content.platform,
        status=provider_result.status,
        post_url=provider_result.permalink or "",
        error=provider_result.provider_message or "",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    db.add(log)

    content.status = provider_result.status
    content.post_id = provider_result.post_id

    await db.commit()
    await db.refresh(content)

    return {
        "content_id": content.id,
        "platform": content.platform,
        "status": content.status,
        "post_id": content.post_id,
        "post_url": provider_result.permalink,
        "message": provider_result.provider_message,
    }
