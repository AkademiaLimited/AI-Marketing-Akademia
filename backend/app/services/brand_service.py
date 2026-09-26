import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brand import BrandProfile

logger = logging.getLogger(__name__)


async def get_active_brand(user_id: str, db: AsyncSession) -> BrandProfile | None:
    """Fetch the active brand profile for a user."""
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.user_id == user_id, BrandProfile.is_active.is_(True))
    )
    return result.scalar_one_or_none()


def build_brand_context(brand: BrandProfile | None) -> str:
    """Build a system prompt prefix from brand profile data.

    This is prepended to every Groq call so AI output stays on-brand.
    Returns an empty string if no brand profile is set.
    """
    if not brand or not brand.voice_description:
        return ""

    parts = [
        f"Brand Voice: {brand.voice_description}.",
        f"Primary Color: {brand.primary_color}.",
        f"Secondary Color: {brand.secondary_color}.",
        f"Font Family: {brand.font_family}.",
    ]

    if brand.tone_keywords:
        parts.append(f"Tone Keywords: {brand.tone_keywords}.")

    return f"""You are writing as part of a brand with the following identity:
{chr(10).join(parts)}

Always match this brand voice, tone, and style in your output.
"""


async def get_brand_context(user_id: str, db: AsyncSession) -> str:
    """Get brand context string for AI calls."""
    brand = await get_active_brand(user_id, db)
    return build_brand_context(brand)
