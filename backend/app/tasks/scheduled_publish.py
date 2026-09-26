import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.providers import get_provider
from app.models.generated_content import GeneratedContent
from app.models.publish_log import PublishLog

logger = logging.getLogger(__name__)


def _get_async_session() -> AsyncSession:
    engine = create_async_engine(settings.database_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker()


async def publish_scheduled_posts() -> dict:
    """Core async logic: publish all posts whose scheduled time has passed."""
    now = datetime.now(timezone.utc).isoformat()
    published = 0
    failed = 0

    async with _get_async_session() as db:
        result = await db.execute(
            select(GeneratedContent).where(
                GeneratedContent.status == "scheduled",
            )
        )
        posts = result.scalars().all()

        for post in posts:
            if post.scheduled_at and post.scheduled_at <= now:
                try:
                    provider = get_provider(post.platform)
                    provider_result = await provider.publish_post({
                        "caption": post.caption,
                        "hashtags": post.hashtags,
                        "call_to_action": post.call_to_action,
                    })

                    log = PublishLog(
                        id=post.id + "_log",
                        product_id=post.product_id,
                        platform=post.platform,
                        status=provider_result.status,
                        post_url=provider_result.permalink or "",
                        error=provider_result.provider_message or "",
                        created_at=now,
                    )
                    db.add(log)

                    post.status = provider_result.status
                    post.post_id = provider_result.post_id
                    published += 1
                except Exception as e:
                    logger.error("Failed to publish scheduled post %s: %s", post.id, e)
                    post.status = "failed"
                    failed += 1

        await db.commit()

    return {"published": published, "failed": failed, "checked": len(posts)}


@celery_app.task
def run_scheduled_publish():
    """Celery task: check and publish all due scheduled posts."""
    result = _run_publish()
    return result


def _run_publish():
    import asyncio
    return asyncio.run(publish_scheduled_posts())
