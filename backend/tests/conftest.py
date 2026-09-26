import os

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_NAME", "test_db")
os.environ.setdefault("SECRET_KEY", "")  # Force random generation in tests

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.brand import BrandProfile
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession):
    from app.core.database import get_db
    from app.api.routers.auth import get_current_admin

    async def override_get_db():
        yield db_session

    async def override_get_current_admin():
        return User(
            id="test-admin",
            email="admin@example.com",
            name="Test Admin",
            hashed_password="test-hash",
            is_active=True,
            is_superuser=True,
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_client(client: AsyncClient):
    return TestClient(app)


@pytest.fixture
async def seed_brand_profile(db_session: AsyncSession):
    brand = BrandProfile(
        id="brand-test-1",
        user_id="test-admin",
        name="Test Brand",
        voice_description="Brand Voice: Professional yet approachable AI marketing tone.",
        primary_color="#1F6F5C",
        secondary_color="#3AAFA9",
        font_family="Inter, sans-serif",
        tone_keywords="professional,approachable,innovative",
        is_active=True,
    )
    db_session.add(brand)
    await db_session.commit()
    await db_session.refresh(brand)
    return brand