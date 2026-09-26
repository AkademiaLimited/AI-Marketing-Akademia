"""
Tests for the marketing pipeline content generation, channel selection, and
publishing tasks. Mocks Groq API calls so no network is needed.
"""
import pytest
from sqlalchemy import select

from app.models.product import Product
from app.models.generated_content import GeneratedContent
from app.models.publish_log import PublishLog


@pytest.fixture
async def seed_business_product(db_session):
    product = Product(
        id="prod-business-1",
        name="AI Pod",
        slug="pod",
        published=True,
        problem="Work scattered across tools",
        target="Teams and departments",
        description="A task management and reporting system with AI built in.",
        features=["Task management"],
        benefits=["Automatic reports"],
        capabilities=[],
        category="business",
        price="$299/mo",
        image_url="",
        marketing_status="pending",
        marketing_result="",
    )
    db_session.add(product)
    await db_session.commit()
    return product


@pytest.fixture
async def seed_general_product(db_session):
    product = Product(
        id="prod-general-1",
        name="AI World",
        slug="world",
        published=True,
        problem="Can't experience places virtually",
        target="Travellers",
        description="A virtual world built around Japan.",
        features=[],
        benefits=[],
        capabilities=[],
        category="general",
        price="$99/mo",
        image_url="",
        marketing_status="pending",
        marketing_result="",
    )
    db_session.add(product)
    await db_session.commit()
    return product


MOCK_CONTENT_RESPONSE = {
    "platforms": {
        "instagram": {
            "caption": "Check out AI Pod for seamless task management!",
            "hashtags": "#ai #productivity #teams",
        },
        "linkedin": {
            "caption": "Introducing AI Pod - automated reporting and task management.",
            "hashtags": "#saas #productivity",
        },
        "email": {
            "caption": "Transform how your team works — AI Pod is here",
            "call_to_action": "Book a demo",
        },
    }
}


MOCK_CHANNEL_RESPONSE = {
    "instagram": 0.85,
    "linkedin": 0.95,
    "twitter": 0.4,
    "email": 0.8,
    "tiktok": 0.2,
    "pinterest": 0.1,
}


async def mock_call_groq_json(prompt, system_prompt, **kwargs):
    if "marketing copywriter" in system_prompt:
        return MOCK_CONTENT_RESPONSE
    if "marketing strategist" in system_prompt:
        return MOCK_CHANNEL_RESPONSE
    return {}


async def mock_call_groq(prompt, system_prompt, **kwargs):
    return "AI-generated reasoning text"


@pytest.mark.anyio
async def test_generate_content_for_product(db_session, seed_business_product, monkeypatch):
    monkeypatch.setattr("app.tasks.content.call_groq_json", mock_call_groq_json)
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import generate_content_for_product

    result = await generate_content_for_product("prod-business-1")

    assert result["product_id"] == "prod-business-1"
    assert result["product_name"] == "AI Pod"
    assert len(result["platforms"]) == 3
    assert "instagram" in result["content_ids"]
    assert "linkedin" in result["content_ids"]
    assert "email" in result["content_ids"]

    gc_result = await db_session.execute(
        select(GeneratedContent).where(GeneratedContent.product_id == "prod-business-1")
    )
    contents = gc_result.scalars().all()
    assert len(contents) == 3
    assert contents[0].platform == "instagram"
    assert "AI Pod" in contents[0].caption


@pytest.mark.anyio
async def test_generate_content_product_not_found(db_session, monkeypatch):
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import generate_content_for_product

    with pytest.raises(ValueError, match="Product nonexistent not found"):
        await generate_content_for_product("nonexistent")


@pytest.mark.anyio
async def test_select_channels_business_rule(db_session, seed_business_product, monkeypatch):
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import select_channels_for_product

    prev_result = {
        "product_id": "prod-business-1",
        "product_name": "AI Pod",
        "content_ids": {"instagram": "c1", "linkedin": "c2"},
    }
    result = await select_channels_for_product(prev_result)

    assert result["channels"] == ["linkedin", "email"]
    assert "content_ids" in result


@pytest.mark.anyio
async def test_select_channels_ai_estimation(db_session, seed_general_product, monkeypatch):
    monkeypatch.setattr("app.tasks.content.call_groq_json", mock_call_groq_json)
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import select_channels_for_product

    seed_general_product.category = "fashion"
    await db_session.commit()

    prev_result = {
        "product_id": "prod-general-1",
        "product_name": "AI World",
        "content_ids": {},
    }
    result = await select_channels_for_product(prev_result)

    assert result["channels"] == ["instagram", "pinterest"]


@pytest.mark.anyio
async def test_publish_content_creates_logs(db_session, seed_business_product, monkeypatch):
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import publish_content_to_channels

    prev_result = {
        "product_id": "prod-business-1",
        "product_name": "AI Pod",
        "channels": ["linkedin", "email"],
        "content_ids": {"linkedin": "c1", "email": "c2"},
    }
    result = await publish_content_to_channels(prev_result)

    assert len(result["publish_results"]) == 2
    for pr in result["publish_results"]:
        assert pr["status"] == "published"
        assert "/linkedin.com/p/" in pr["url"] or "/email.com/p/" in pr["url"]

    pub_result = await db_session.execute(
        select(PublishLog).where(PublishLog.product_id == "prod-business-1")
    )
    logs = pub_result.scalars().all()
    assert len(logs) == 2
    assert all(log.status == "published" for log in logs)

    prod_result = await db_session.execute(
        select(Product).where(Product.id == "prod-business-1")
    )
    product = prod_result.scalar_one()
    assert product.marketing_status == "completed"
    assert "Published to 2 channels" in product.marketing_result


@pytest.mark.anyio
async def test_generate_content_with_brand_context(
    db_session, seed_business_product, monkeypatch, seed_brand_profile,
):
    monkeypatch.setattr("app.tasks.content.call_groq_json", mock_call_groq_json)
    monkeypatch.setattr("app.tasks.content._get_async_session", lambda: db_session)

    from app.tasks.content import generate_content_for_product

    result = await generate_content_for_product("prod-business-1", user_id=seed_brand_profile.user_id)

    assert result["brand_context"]
    assert "Brand Voice" in result["brand_context"]
