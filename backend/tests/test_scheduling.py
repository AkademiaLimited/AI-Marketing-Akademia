import pytest
from httpx import AsyncClient

from app.core.providers.schemas import PostResponse
from app.core.providers import get_provider, MockProvider


@pytest.mark.anyio
async def test_list_scheduled_posts_empty(client: AsyncClient):
    response = await client.get("/api/scheduling/scheduled")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.anyio
async def test_schedule_post_success(client: AsyncClient):
    # Create a product first (needed for GeneratedContent FK)
    product_payload = {
        "id": "prod-sched",
        "name": "Schedule Test Product",
        "slug": "schedule-test",
        "published": True,
        "problem": "P",
        "target": "T",
        "description": "D",
        "features": [],
        "benefits": [],
    }
    await client.post("/api/products/", json=product_payload)

    # Create generated content
    content_payload = {
        "id": "gc-1",
        "product_id": "prod-sched",
        "platform": "twitter",
        "caption": "Test scheduled post",
        "hashtags": "#test",
        "call_to_action": "Learn more",
        "status": "generated",
    }

    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app
    from sqlalchemy import select

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(**content_payload))
        await db.commit()

    # Schedule it
    when = "2026-12-25T10:00:00+00:00"
    response = await client.post(
        "/api/scheduling/schedule",
        json={"content_id": "gc-1", "when": when},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "scheduled"
    assert data["scheduled_at"] == when


@pytest.mark.anyio
async def test_schedule_post_not_found(client: AsyncClient):
    when = "2026-12-25T10:00:00+00:00"
    response = await client.post(
        "/api/scheduling/schedule",
        json={"content_id": "nonexistent", "when": when},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_schedule_post_wrong_status(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-pending",
            product_id="prod-sched",
            platform="twitter",
            caption="Pending post",
            status="pending",
        ))
        await db.commit()

    response = await client.post(
        "/api/scheduling/schedule",
        json={"content_id": "gc-pending", "when": "2026-12-25T10:00:00+00:00"},
    )
    assert response.status_code == 400
    assert "Cannot schedule" in response.json()["detail"]


@pytest.mark.anyio
async def test_schedule_post_past_date_rejected(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-past",
            product_id="prod-sched",
            platform="twitter",
            caption="Past post",
            status="generated",
        ))
        await db.commit()

    response = await client.post(
        "/api/scheduling/schedule",
        json={"content_id": "gc-past", "when": "2020-01-01T00:00:00+00:00"},
    )
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()


@pytest.mark.anyio
async def test_schedule_post_invalid_datetime(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-bad-dt",
            product_id="prod-sched",
            platform="twitter",
            caption="Bad datetime",
            status="generated",
        ))
        await db.commit()

    response = await client.post(
        "/api/scheduling/schedule",
        json={"content_id": "gc-bad-dt", "when": "not-a-date"},
    )
    assert response.status_code == 400
    assert "Invalid datetime format" in response.json()["detail"]


@pytest.mark.anyio
async def test_publish_now_success(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-publish",
            product_id="prod-sched",
            platform="twitter",
            caption="Ready to publish",
            hashtags="#test",
            call_to_action="Learn more",
            status="generated",
        ))
        await db.commit()

    response = await client.post(
        "/api/scheduling/publish",
        json={"content_id": "gc-publish"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"
    assert data["post_id"].startswith("mock_")
    assert "twitter.com" in data["post_url"]


@pytest.mark.anyio
async def test_publish_now_not_found(client: AsyncClient):
    response = await client.post(
        "/api/scheduling/publish",
        json={"content_id": "nonexistent"},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_publish_now_wrong_status(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-failed",
            product_id="prod-sched",
            platform="twitter",
            caption="Failed post",
            status="failed",
        ))
        await db.commit()

    response = await client.post(
        "/api/scheduling/publish",
        json={"content_id": "gc-failed"},
    )
    assert response.status_code == 400
    assert "failed" in response.json()["detail"]


def test_mock_provider_publish_post():
    provider = MockProvider("instagram")

    import asyncio
    result = asyncio.run(provider.publish_post({"caption": "test"}))

    assert isinstance(result, PostResponse)
    assert result.status == "published"
    assert "instagram" in result.permalink


@pytest.mark.anyio
async def test_scheduled_posts_appear_in_list(client: AsyncClient):
    from app.models.generated_content import GeneratedContent
    from app.core.database import get_db
    from app.main import app

    async for db in app.dependency_overrides[get_db]():
        db.add(GeneratedContent(
            id="gc-list",
            product_id="prod-sched",
            platform="twitter",
            caption="List item",
            status="scheduled",
            scheduled_at="2026-12-25T10:00:00+00:00",
        ))
        await db.commit()

    response = await client.get("/api/scheduling/scheduled")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(p["content_id"] == "gc-list" for p in data)