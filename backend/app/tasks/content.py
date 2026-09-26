import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai.groq_client import call_groq, call_groq_json
from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.generated_content import GeneratedContent
from app.models.product import Product
from app.models.publish_log import PublishLog
from app.services.brand_service import get_brand_context

logger = logging.getLogger(__name__)


def _get_async_session() -> AsyncSession:
    """Create a fresh engine and session for use in Celery tasks."""
    engine = create_async_engine(settings.database_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker()


SYSTEM_PROMPT_CONTENT = """
You are an expert AI marketing copywriter. Generate engaging, platform-specific
marketing content for the given product. Return ONLY valid JSON with no
explanatory text outside the JSON.

Format:
{
  "platforms": {
    "instagram": {
      "caption": "engaging caption text",
      "hashtags": "#hashtag1 #hashtag2 #hashtag3"
    },
    "linkedin": {
      "caption": "professional announcement text",
      "hashtags": "#hashtag1 #hashtag2"
    },
    "twitter": {
      "caption": "short announcement under 280 chars",
      "hashtags": "#hashtag1 #hashtag2"
    },
    "email": {
      "caption": "email subject line",
      "call_to_action": "click here to learn more"
    }
  }
}
"""

SYSTEM_PROMPT_CHANNEL = """
You are an expert marketing strategist. Based on the product category and
description, return ONLY valid JSON indicating the estimated reach quality
(0.0 to 1.0) for each potential channel. Higher means better fit.

Format:
{
  "instagram": 0.8,
  "linkedin": 0.9,
  "twitter": 0.6,
  "email": 0.7,
  "tiktok": 0.4,
  "pinterest": 0.3
}
"""


CHANNEL_RULES = {
    "fashion": ["instagram", "pinterest"],
    "general": ["twitter", "tiktok"],
    "business": ["linkedin", "email"],
}


async def _generate_content_for_product(
    product: Product, brand_context: str = ""
) -> dict:
    prompt = (
        f"Product: {product.name}\n"
        f"Category: {product.category}\n"
        f"Price: {product.price}\n"
        f"Description: {product.description}\n"
        f"Features: {', '.join(product.features) if product.features else 'N/A'}\n"
        f"Benefits: {', '.join(product.benefits) if product.benefits else 'N/A'}\n"
        f"Problem it solves: {product.problem}\n"
        f"Target audience: {product.target}\n\n"
        f"Generate engaging marketing content for this product."
    )

    result = await call_groq_json(
        prompt, system_prompt=SYSTEM_PROMPT_CONTENT, brand_context=brand_context or None
    )
    return result


async def _select_channels_for_product(
    product: Product, brand_context: str = ""
) -> list[str]:
    category = product.category or "general"
    if category in CHANNEL_RULES:
        return CHANNEL_RULES[category]

    prompt = (
        f"Product: {product.name}\n"
        f"Category: {category}\n"
        f"Description: {product.description}\n\n"
        f"Which marketing channels would this product perform best on? "
        f"Return estimates for: instagram, linkedin, twitter, email, tiktok, pinterest."
    )

    estimates = await call_groq_json(
        prompt, system_prompt=SYSTEM_PROMPT_CHANNEL, brand_context=brand_context or None
    )

    if isinstance(estimates, dict):
        sorted_channels = sorted(
            [(k, v) for k, v in estimates.items() if isinstance(v, (int, float)) and v > 0.5],
            key=lambda x: x[1],
            reverse=True,
        )
        return [ch for ch, _ in sorted_channels]

    return ["email"]


async def _publish_to_platform(
    db: AsyncSession,
    product: Product,
    content: GeneratedContent,
    platform: str,
) -> PublishLog:
    """Simulate publishing to a social media platform or email service.

    NOTE: When real provider APIs are integrated, replace the URL fabrication
    with actual API calls via get_provider(platform).
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    publish_log = PublishLog(
        id=str(uuid.uuid4()),
        product_id=product.id,
        platform=platform,
        status="pending",
        created_at=timestamp,
    )
    db.add(publish_log)
    await db.commit()

    try:
        post_url = f"https://{platform}.com/p/{uuid.uuid4().hex[:12]}"
        publish_log.status = "published"
        publish_log.post_url = post_url
        await db.commit()

        logger.info("Published product %s to %s: %s", product.id, platform, post_url)
    except Exception as e:
        publish_log.status = "failed"
        publish_log.error = str(e)
        await db.commit()
        logger.error("Failed to publish %s to %s: %s", product.id, platform, e)

    return publish_log


async def generate_content_for_product(product_id: str, user_id: str | None = None) -> dict:
    """
    Core async logic: generate AI marketing content for a product.

    Optionally fetches brand context for the given user_id and injects it
    into the Groq system prompt so generated content stays on-brand.
    """
    async with _get_async_session() as db:
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {product_id} not found")

        brand_context = ""
        if user_id:
            brand_context = await get_brand_context(user_id, db)

        content_data = await _generate_content_for_product(product, brand_context)
        platforms = content_data.get("platforms", {})

        created = {}
        for platform, data in platforms.items():
            gc = GeneratedContent(
                id=str(uuid.uuid4()),
                product_id=product.id,
                platform=platform,
                caption=data.get("caption", ""),
                hashtags=data.get("hashtags", ""),
                call_to_action=data.get("call_to_action", ""),
                status="generated",
            )
            db.add(gc)
            created[platform] = gc.id

        await db.commit()
        return {
            "product_id": product_id,
            "product_name": product.name,
            "platforms": list(platforms.keys()),
            "content_ids": created,
            "brand_context": brand_context,
        }


async def select_channels_for_product(prev_result: dict) -> dict:
    """
    Core async logic: select target channels for a product.

    Receives brand_context from the generate_content stage and passes it
    through to keep AI calls consistent.
    """
    async with _get_async_session() as db:
        result = await db.execute(
            select(Product).where(Product.id == prev_result["product_id"])
        )
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {prev_result['product_id']} not found")

        brand_context = prev_result.get("brand_context", "")
        channels = await _select_channels_for_product(product, brand_context)

        return {
            "product_id": prev_result["product_id"],
            "product_name": prev_result["product_name"],
            "channels": channels,
            "content_ids": prev_result["content_ids"],
            "brand_context": brand_context,
        }


async def publish_content_to_channels(prev_result: dict) -> dict:
    """
    Core async logic: auto-publish generated content to selected channels.
    """
    async with _get_async_session() as db:
        result = await db.execute(
            select(Product).where(Product.id == prev_result["product_id"])
        )
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product {prev_result['product_id']} not found")

        content_ids = prev_result["content_ids"]
        channels = prev_result["channels"]

        logs = []
        for platform in channels:
            if platform not in content_ids:
                content = GeneratedContent(
                    id=str(uuid.uuid4()),
                    product_id=product.id,
                    platform=platform,
                    caption="",
                    hashtags="",
                    call_to_action="",
                    status="placeholder",
                )
                db.add(content)
                await db.commit()
                content_ids[platform] = content.id

            content_result = await db.execute(
                select(GeneratedContent).where(GeneratedContent.id == content_ids[platform])
            )
            content = content_result.scalar_one_or_none()

            log = await _publish_to_platform(db, product, content, platform)
            logs.append({"platform": platform, "status": log.status, "url": log.post_url})

        product.marketing_status = "completed"
        product.marketing_result = f"Published to {len(channels)} channels: {', '.join(channels)}"
        await db.commit()

        return {
            "product_id": prev_result["product_id"],
            "product_name": prev_result.get("product_name", product.name),
            "publish_results": logs,
        }


@celery_app.task(bind=True)
def generate_content(self, product_id: str, user_id: str | None = None) -> dict:
    """
    Worker 1: Generate AI marketing content for a product.

    Calls Groq to produce platform-specific captions and hashtags,
    saves them to the database. Injects brand context if user_id is provided.
    """
    self.update_state(state="STARTED")
    result = asyncio.run(generate_content_for_product(product_id, user_id))
    self.update_state(state="SUCCESS", meta=result)
    return result


@celery_app.task(bind=True)
def select_channels(self, prev_result: dict) -> dict:
    """
    Worker 2: Select target channels for the product based on category.

    Receives result from generate_content task (including brand_context
    if provided) and determines which platforms to publish to.
    """
    self.update_state(state="STARTED")
    result = asyncio.run(select_channels_for_product(prev_result))
    self.update_state(state="SUCCESS", meta=result)
    return result


@celery_app.task(bind=True)
def publish_content(self, prev_result: dict) -> dict:
    """
    Worker 3: Auto-publish generated content to selected channels.

    Connects to platform providers (simulated via MockProvider by default)
    and publishes the product posts.
    """
    self.update_state(state="STARTED")
    result = asyncio.run(publish_content_to_channels(prev_result))
    self.update_state(state="SUCCESS", meta=result)
    return result
