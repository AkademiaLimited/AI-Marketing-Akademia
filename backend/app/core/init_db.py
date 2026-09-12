import asyncio
import logging

from app.core.database import AsyncSessionLocal, Base, engine
from app.core.config import settings
from app.core.seed import (
    seed_automations,
    seed_campaigns,
    seed_content,
    seed_emails,
    seed_leads,
    seed_products,
    seed_users,
)

logger = logging.getLogger(__name__)


async def initialize_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        if settings.demo_data:
            await seed_products(db)
            await seed_leads(db)
            await seed_campaigns(db)
            await seed_emails(db)
            await seed_automations(db)
            await seed_content(db)
        await seed_users(db)


async def initialize_with_retries(attempts: int = 12, delay_seconds: int = 2) -> None:
    for attempt in range(1, attempts + 1):
        try:
            await initialize_database()
            logger.info("Database schema and seed data are ready")
            return
        except Exception:
            if attempt == attempts:
                logger.exception("Database initialization failed after %s attempts", attempts)
                raise
            logger.warning(
                "Database is not ready (attempt %s/%s); retrying in %s seconds",
                attempt,
                attempts,
                delay_seconds,
            )
            await asyncio.sleep(delay_seconds)


if __name__ == "__main__":
    asyncio.run(initialize_with_retries())