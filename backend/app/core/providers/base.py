from abc import ABC, abstractmethod
from typing import Any


class AbstractProvider(ABC):
    """Base interface for all social/publishing platform providers.

    Every provider implements the same interface so that the rest of
    the system can call publishing, scheduling, engagement, and inbox
    operations without knowing whether it is talking to a real API
    or a mock.
    """

    platform: str

    @abstractmethod
    async def publish_post(self, content: dict[str, Any]) -> dict[str, Any]:
        """Publish a post immediately.

        Args:
            content: Dict with caption, hashtags, call_to_action, image_url, etc.

        Returns:
            Dict with post_id, permalink, and any provider-specific metadata.
        """

    @abstractmethod
    async def schedule_post(self, content: dict[str, Any], when: str) -> dict[str, Any]:
        """Schedule a post for future publication.

        Args:
            content: Same dict as publish_post.
            when: ISO-8601 timestamp for publishing.

        Returns:
            Dict with post_id, scheduled_at, and any provider-specific metadata.
        """

    @abstractmethod
    async def get_post_status(self, post_id: str) -> dict[str, Any]:
        """Check the status of a published or scheduled post.

        Returns:
            Dict with status (published/scheduled/failed), metrics, etc.
        """

    @abstractmethod
    async def get_engagement(self, post_id: str) -> dict[str, Any]:
        """Fetch engagement metrics for a post.

        Returns:
            Dict with impressions, engagements, clicks, likes, shares, etc.
        """

    @abstractmethod
    async def get_messages(self, since: str | None = None) -> list[dict[str, Any]]:
        """Fetch messages/inbox items from the platform.

        Args:
            since: ISO-8601 timestamp to fetch messages after.

        Returns:
            List of message dicts with id, sender, content, timestamp, etc.
        """
