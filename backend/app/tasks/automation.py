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
from app.models.automation import Automation
from app.models.lead import Lead
from app.models.product import Product
from app.services.brand_service import get_brand_context

logger = logging.getLogger(__name__)


def _get_async_session() -> AsyncSession:
    """Create a fresh engine and session for use in Celery tasks."""
    engine = create_async_engine(settings.database_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return session_maker()


SYSTEM_PROMPT_DISCOVER = """
You are an AI marketing assistant. Your job is to discover realistic potential
leads for a B2B marketing team. Given a product description and target
industry, generate 3 candidate lead companies with:
- company name
- website URL
- industry
- location (city, country)
- a plausible contact person (full name)
- their email address (synthetic but realistic)
- a brief description of the business problem they might have that our product solves

Return ONLY valid JSON in this exact format:
[
  {
    "company": "string",
    "website": "string",
    "industry": "string",
    "location": "string",
    "contact": "string",
    "email": "string",
    "problem": "string"
  }
]
"""


async def _get_leads_for_product(product: Product, brand_context: str = "") -> list[dict]:
    target_industry = product.target or "technology"
    problem = product.problem or "needs AI solutions"

    prompt = (
        f"Product: {product.name}\n"
        f"Problem it solves: {problem}\n"
        f"Primary target: {target_industry}\n\n"
        f"Generate 3 realistic B2B prospects in the {target_industry} industry "
        f"who could benefit from {product.name}."
    )

    result = await call_groq_json(
        prompt, system_prompt=SYSTEM_PROMPT_DISCOVER, brand_context=brand_context or None
    )
    if isinstance(result, list):
        return result
    return result.get("leads", [])


async def _analyze_and_store_lead(
    db: AsyncSession, lead_data: dict, product: Product, brand_context: str = ""
) -> Lead:
    reasoning_prompt = (
        f"Company: {lead_data['company']}\n"
        f"Industry: {lead_data['industry']}\n"
        f"Problem: {lead_data['problem']}\n"
        f"Product: {product.name}\n"
        f"Product description: {product.description}\n\n"
        f"In 2-3 sentences, explain why this company is a good fit "
        f"for {product.name} and what specific value they would get."
    )

    reasoning = await call_groq(
        reasoning_prompt,
        system_prompt="You are a B2B marketing strategist. Give concise reasoning.",
        brand_context=brand_context or None,
        max_tokens=512,
    )

    lead = Lead(
        id=str(uuid.uuid4()),
        company=lead_data["company"],
        website=lead_data.get("website", ""),
        industry=lead_data.get("industry", ""),
        location=lead_data.get("location", ""),
        contact=lead_data.get("contact", ""),
        email=lead_data.get("email", ""),
        product_id=product.id,
        status="new",
        problem=lead_data.get("problem", ""),
        reasoning=reasoning or "",
        last_contact="",
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


async def discover_leads_for_product(product_slug: str, user_id: str | None = None) -> dict:
    """
    Core async logic: discover new leads for a product using AI.

    Optionally fetches brand context for the given user_id and injects it
    into the Groq system prompt so generated leads align with brand voice.

    Can be called directly in tests. The Celery task wraps this with asyncio.run.
    """
    async with _get_async_session() as db:
        product_result = await db.execute(
            select(Product).where(Product.slug == product_slug)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product with slug '{product_slug}' not found")

        brand_context = ""
        if user_id:
            brand_context = await get_brand_context(user_id, db)

        leads = await _get_leads_for_product(product, brand_context)
        created = []
        for lead_data in leads:
            lead = await _analyze_and_store_lead(db, lead_data, product, brand_context)
            created.append(lead.id)

        timestamp = datetime.now(timezone.utc).isoformat()

        automation_result = (
            f"Discovered {len(created)} new leads for '{product.name}'. "
            f"Lead IDs: {', '.join(created[:5])}"
        )

        automation_result_row = await db.execute(
            select(Automation).where(Automation.id == "A1")
        )
        automation = automation_result_row.scalar_one_or_none()
        if automation:
            automation.last_run = timestamp
            automation.result = automation_result
            await db.commit()

        return {
            "product": product.name,
            "leads_found": len(created),
            "lead_ids": created,
            "timestamp": timestamp,
        }


@celery_app.task(bind=True)
def run_lead_discovery(self, product_slug: str, user_id: str | None = None) -> dict:
    """
    Celery task: Discover new leads for a given product using AI.

    Args:
        product_slug: The slug of the product to run discovery for.
        user_id: Optional user ID to fetch brand context for on-brand lead generation.

    Returns:
        Dict with summary: {"product": str, "leads_found": int, "timestamp": str}
    """
    self.update_state(state="STARTED")
    result = asyncio.run(discover_leads_for_product(product_slug, user_id))
    self.update_state(
        state="SUCCESS",
        meta=result,
    )
    return result
