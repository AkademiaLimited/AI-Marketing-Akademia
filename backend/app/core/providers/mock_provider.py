import uuid
from datetime import datetime, timezone

from app.core.providers.base import AbstractProvider
from app.core.providers.schemas import (
    EngagementResponse,
    MessageResponse,
    PostResponse,
)


class MockProvider(AbstractProvider):
    """Simulated provider that mimics real API behavior without
    requiring actual credentials. This is the default when no
    platform API keys are configured."""

    def __init__(self, platform: str):
        self.platform = platform

    def _fake_url(self) -> str:
        return f"https://{self.platform}.com/p/{uuid.uuid4().hex[:12]}"

    async def publish_post(self, content: dict) -> PostResponse:
        return PostResponse(
            post_id=f"mock_{uuid.uuid4().hex[:8]}",
            platform=self.platform,
            status="published",
            permalink=self._fake_url(),
            provider_message="Published (simulated)",
            raw={"id": f"mock_{uuid.uuid4().hex[:8]}"},
        )

    async def schedule_post(self, content: dict, when: str) -> PostResponse:
        scheduled_at = datetime.fromisoformat(when) if when else datetime.now(timezone.utc)
        scheduled_iso = scheduled_at.isoformat()
        return PostResponse(
            post_id=f"mock_scheduled_{uuid.uuid4().hex[:8]}",
            platform=self.platform,
            status="scheduled",
            permalink=self._fake_url(),
            provider_message=f"Scheduled for {scheduled_iso} (simulated)",
            raw={"scheduled_at": scheduled_iso},
        )

    async def get_post_status(self, post_id: str) -> PostResponse:
        return PostResponse(
            post_id=post_id,
            platform=self.platform,
            status="published",
            permalink=self._fake_url(),
            raw={},
        )

    async def get_engagement(self, post_id: str) -> EngagementResponse:
        import random

        base = random.randint(100, 5000)
        engaged = random.randint(base // 10, base // 3)
        return EngagementResponse(
            post_id=post_id,
            platform=self.platform,
            impressions=base,
            engagements=engaged,
            clicks=random.randint(engaged // 10, engaged // 2),
            likes=random.randint(engaged // 3, engaged),
            shares=random.randint(1, engaged // 10),
            comments=random.randint(2, engaged // 20),
            saved=random.randint(0, engaged // 15),
            raw={"mock": True},
        )

    async def get_messages(self, since: str | None = None) -> list[MessageResponse]:
        return []
