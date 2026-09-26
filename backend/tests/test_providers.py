import pytest

from app.core.providers import AbstractProvider, MockProvider, get_provider
from app.core.providers.schemas import (
    EngagementResponse,
    MessageResponse,
    PostResponse,
)


def test_mock_provider_implements_abstract_methods():
    provider = MockProvider("instagram")
    assert isinstance(provider, AbstractProvider)


def test_get_provider_returns_mock_by_default():
    provider = get_provider("instagram")
    assert isinstance(provider, MockProvider)
    assert provider.platform == "instagram"


def test_get_provider_require_real_raises():
    with pytest.raises(NotImplementedError, match="Real instagram provider not yet implemented"):
        get_provider("instagram", require_real=True)


@pytest.mark.anyio
async def test_mock_publish_post_returns_post_response():
    provider = MockProvider("twitter")
    content = {"caption": "Hello world", "hashtags": ["#test"], "call_to_action": "Click here"}
    result = await provider.publish_post(content)

    assert isinstance(result, PostResponse)
    assert result.platform == "twitter"
    assert result.status == "published"
    assert result.post_id.startswith("mock_")
    assert result.permalink is not None
    assert "twitter.com" in result.permalink


@pytest.mark.anyio
async def test_mock_schedule_post_returns_scheduled_status():
    provider = MockProvider("linkedin")
    content = {"caption": "Scheduled post", "hashtags": []}
    when = "2026-12-25T10:00:00+00:00"

    result = await provider.schedule_post(content, when)

    assert isinstance(result, PostResponse)
    assert result.status == "scheduled"
    assert result.post_id.startswith("mock_scheduled_")
    assert "Scheduled for" in result.provider_message


@pytest.mark.anyio
async def test_mock_get_post_status():
    provider = MockProvider("facebook")
    result = await provider.get_post_status("some_post_id")

    assert result.post_id == "some_post_id"
    assert result.platform == "facebook"
    assert result.status == "published"


@pytest.mark.anyio
async def test_mock_get_engagement_returns_numeric_metrics():
    provider = MockProvider("instagram")
    result = await provider.get_engagement("post_123")

    assert isinstance(result, EngagementResponse)
    assert result.post_id == "post_123"
    assert result.platform == "instagram"
    assert result.impressions >= 100
    assert result.impressions <= 5000
    assert result.engagements > 0
    assert result.likes > 0


@pytest.mark.anyio
async def test_mock_get_messages_returns_empty_list():
    provider = MockProvider("discord")
    result = await provider.get_messages()

    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.anyio
async def test_mock_provider_works_for_all_platforms():
    platforms = ["instagram", "linkedin", "twitter", "tiktok", "email", "discord", "slack"]

    for platform in platforms:
        provider = get_provider(platform)
        assert provider.platform == platform

        result = await provider.publish_post({"caption": "test"})
        assert result.status == "published"
        assert platform in result.permalink
