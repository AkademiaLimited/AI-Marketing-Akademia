import pytest
from httpx import AsyncClient

from app.models.brand import BrandProfile
from app.services.brand_service import build_brand_context, get_brand_context, get_active_brand


@pytest.fixture
async def brand(db_session):
    """Create a brand profile for testing."""
    b = BrandProfile(
        id="brand-1",
        user_id="admin@akademia.local",
        name="Akademia Brand",
        voice_description="Professional but approachable, focused on practical AI advice",
        primary_color="#1F6F5C",
        secondary_color="#3AAFA9",
        font_family="Inter, sans-serif",
        tone_keywords="helpful, clear, direct",
        is_active=True,
    )
    db_session.add(b)
    await db_session.commit()
    await db_session.refresh(b)
    return b


@pytest.fixture
async def inactive_brand(db_session):
    """Create an inactive brand profile for testing."""
    b = BrandProfile(
        id="brand-inactive",
        user_id="test@example.com",
        name="Inactive Brand",
        voice_description="Test",
        is_active=False,
    )
    db_session.add(b)
    await db_session.commit()
    await db_session.refresh(b)
    return b


# ── Brand Profile CRUD Tests ──────────────────────────────


@pytest.mark.anyio
async def test_list_brands(client: AsyncClient, brand):
    response = await client.get("/api/brands/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(b["name"] == "Akademia Brand" for b in data)


@pytest.mark.anyio
async def test_list_brands_filtered_by_user(client: AsyncClient, brand, inactive_brand):
    response = await client.get("/api/brands/?user_id=admin@akademia.local")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Akademia Brand"


@pytest.mark.anyio
async def test_get_brand_by_id(client: AsyncClient, brand):
    response = await client.get(f"/api/brands/{brand.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Akademia Brand"
    assert data["voice_description"] == "Professional but approachable, focused on practical AI advice"


@pytest.mark.anyio
async def test_get_brand_not_found(client: AsyncClient):
    response = await client.get("/api/brands/nonexistent")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_user_active_brand(client: AsyncClient, brand):
    response = await client.get("/api/brands/user/admin@akademia.local")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert data["user_id"] == "admin@akademia.local"


@pytest.mark.anyio
async def test_get_user_brand_not_found(client: AsyncClient):
    response = await client.get("/api/brands/user/nonexistent")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_brand(client: AsyncClient):
    import uuid
    payload = {
        "name": "Test Brand",
        "voice_description": "Casual and fun",
        "primary_color": "#FF5733",
        "secondary_color": "#C70039",
        "font_family": "Arial",
        "tone_keywords": "fun, casual, young",
        "is_active": True,
    }
    response = await client.post(
        "/api/brands/?user_id=test-user-123",
        json=payload,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Brand"
    assert data["user_id"] == "test-user-123"
    assert data["primary_color"] == "#FF5733"


@pytest.mark.anyio
async def test_update_brand(client: AsyncClient, brand):
    response = await client.patch(
        f"/api/brands/{brand.id}",
        json={"name": "Updated Brand Name", "tone_keywords": "professional, concise"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Brand Name"
    assert data["tone_keywords"] == "professional, concise"
    assert data["voice_description"] == brand.voice_description


@pytest.mark.anyio
async def test_update_brand_not_found(client: AsyncClient):
    response = await client.patch(
        "/api/brands/nonexistent",
        json={"name": "Updated"},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_brand(client: AsyncClient, brand):
    response = await client.delete(f"/api/brands/{brand.id}")
    assert response.status_code == 204

    response = await client.get(f"/api/brands/{brand.id}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_brand_not_found(client: AsyncClient):
    response = await client.delete("/api/brands/nonexistent")
    assert response.status_code == 404


# ── Brand Context Service Tests ──────────────────────────


@pytest.mark.anyio
async def test_get_active_brand_returns_active(db_session, brand, inactive_brand):
    result = await get_active_brand("admin@akademia.local", db_session)
    assert result is not None
    assert result.id == "brand-1"
    assert result.is_active is True


@pytest.mark.anyio
async def test_get_active_brand_returns_none_for_inactive_only(db_session, inactive_brand):
    result = await get_active_brand("test@example.com", db_session)
    assert result is None


@pytest.mark.anyio
async def test_get_active_brand_returns_none_for_no_user(db_session):
    result = await get_active_brand("nonexistent@user.com", db_session)
    assert result is None


def test_build_brand_context_with_brand():
    brand = BrandProfile(
        id="b1",
        user_id="test",
        name="Test Brand",
        voice_description="Professional but approachable",
        primary_color="#1F6F5C",
        secondary_color="#3AAFA9",
        font_family="Inter, sans-serif",
        tone_keywords="helpful, clear, direct",
        is_active=True,
    )
    context = build_brand_context(brand)

    assert "Brand Voice: Professional but approachable" in context
    assert "Primary Color: #1F6F5C" in context
    assert "Tone Keywords: helpful, clear, direct" in context
    assert "match this brand voice" in context


def test_build_brand_context_empty_for_none():
    assert build_brand_context(None) == ""


def test_build_brand_context_empty_for_no_voice():
    brand = BrandProfile(
        id="b2",
        user_id="test",
        name="No Voice",
        voice_description="",
    )
    assert build_brand_context(brand) == ""


@pytest.mark.anyio
async def test_get_brand_context_returns_string(db_session, brand):
    context = await get_brand_context("admin@akademia.local", db_session)
    assert "Brand Voice" in context
    assert "Professional but approachable" in context


@pytest.mark.anyio
async def test_get_brand_context_empty_for_no_brand(db_session):
    context = await get_brand_context("nonexistent@user.com", db_session)
    assert context == ""


# ── Brand Profile Defaults Tests ─────────────────────────


def test_brand_profile_defaults():
    """Verify default values match Ocoya-style brand identity settings."""
    from app.schemas.brand import BrandProfileBase
    defaults = BrandProfileBase().model_dump()
    assert defaults["name"] == "Default Brand"
    assert defaults["primary_color"] == "#1F6F5C"
    assert defaults["secondary_color"] == "#3AAFA9"
    assert defaults["font_family"] == "Inter, sans-serif"
    assert defaults["is_active"] is True
