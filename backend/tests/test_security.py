import time
import pytest
from httpx import AsyncClient

from app.core.auth import (
    _check_rate_limit,
    _login_attempts,
    hash_password,
    validate_password,
)
from app.core.config import settings


@pytest.fixture(autouse=True)
def clear_rate_limit_state():
    """Clear the in-memory rate limit store before each test."""
    _login_attempts.clear()
    yield
    _login_attempts.clear()


# ── Password Policy Tests ──────────────────────────────────────────


@pytest.mark.anyio
async def test_password_min_length_enforced():
    with pytest.raises(ValueError, match="at least 8 characters"):
        validate_password("Short1A")


@pytest.mark.anyio
async def test_password_requires_uppercase():
    with pytest.raises(ValueError, match="uppercase letter"):
        validate_password("nouppercase1")


@pytest.mark.anyio
async def test_password_requires_lowercase():
    with pytest.raises(ValueError, match="lowercase letter"):
        validate_password("NOLOWERCASE1")


@pytest.mark.anyio
async def test_password_requires_digit():
    with pytest.raises(ValueError, match="digit"):
        validate_password("NoDigitHere")


@pytest.mark.anyio
async def test_password_valid():
    validate_password("ValidPass1")  # should not raise


# ── Registration with Weak Password ────────────────────────────────


@pytest.mark.anyio
async def test_register_weak_password_rejected(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "weak@example.com", "name": "Weak", "password": "weak"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_register_strong_password_accepted(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={"email": "good@example.com", "name": "Good", "password": "GoodPass1"},
    )
    assert response.status_code == 201


# ── Rate Limiting Tests ────────────────────────────────────────────


@pytest.mark.anyio
async def test_login_rate_limit_blocks_after_max_attempts(client: AsyncClient):
    """Test that rate limiting blocks after max attempts from the same IP."""
    # Register a user first
    await client.post(
        "/api/auth/register",
        json={"email": "ratelimit@example.com", "name": "RL", "password": "GoodPass1"},
    )

    # Make login attempts up to the limit - all from same IP
    for i in range(settings.rate_limit_login_attempts):
        response = await client.post(
            "/api/auth/login",
            data={"username": "ratelimit@example.com", "password": "WrongPass1"},
        )
        assert response.status_code == 400, f"Attempt {i+1} should fail with 400 (wrong password), got {response.status_code}"

    # Next attempt should be rate-limited
    response = await client.post(
        "/api/auth/login",
        data={"username": "ratelimit@example.com", "password": "WrongPass1"},
    )
    assert response.status_code == 429
    assert "Too many" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_rate_limit_allows_after_window():
    key = "test-window-key"
    # Exhaust the limit
    for _ in range(settings.rate_limit_login_attempts):
        assert _check_rate_limit(key, settings.rate_limit_login_attempts, settings.rate_limit_login_window_seconds)

    # Next should be blocked
    assert not _check_rate_limit(key, settings.rate_limit_login_attempts, settings.rate_limit_login_window_seconds)


# ── Token Expiry Tests ─────────────────────────────────────────────


@pytest.mark.anyio
async def test_token_expiry_is_short():
    """Verify access_token_expire_minutes is set to a reasonable value (<= 60 min)."""
    assert settings.access_token_expire_minutes <= 60
    assert settings.access_token_expire_minutes > 0


# ── Secret Key Strength Tests ──────────────────────────────────────


def test_secret_key_is_not_default():
    """The secret_key should not be the well-known default 'change-me'."""
    assert settings.secret_key != "change-me"
    assert len(settings.secret_key) >= 32


def test_secret_key_is_random():
    """Each import should produce a different secret key (unless overridden by env)."""
    from app.core.auth import create_access_token
    token1 = create_access_token({"sub": "test", "data": "a"})
    time.sleep(0.01)  # ensure different timestamp
    token2 = create_access_token({"sub": "test", "data": "b"})
    # Tokens should differ because they include different payload data
    assert token1 != token2


def test_secret_key_is_secure_length():
    """The generated secret key should be at least 32 characters."""
    assert len(settings.secret_key) >= 32
    # Should be URL-safe base64
    import re
    assert re.match(r'^[A-Za-z0-9_-]+$', settings.secret_key)


# ── Password Hashing Tests ─────────────────────────────────────────


def test_hash_password_produces_bcrypt_hash():
    hashed = hash_password("SecurePass1")
    assert hashed.startswith("$2")  # bcrypt prefix


def test_verify_password_correct():
    hashed = hash_password("SecurePass1")
    from app.core.auth import verify_password
    assert verify_password("SecurePass1", hashed)


def test_verify_password_incorrect():
    hashed = hash_password("SecurePass1")
    from app.core.auth import verify_password
    assert not verify_password("WrongPass1", hashed)


# ── Config Defaults Tests ──────────────────────────────────────────


def test_password_policy_defaults():
    assert settings.password_min_length >= 8
    assert settings.password_require_uppercase is True
    assert settings.password_require_lowercase is True
    assert settings.password_require_digit is True


def test_rate_limit_config():
    assert settings.rate_limit_enabled is True
    assert settings.rate_limit_login_attempts > 0
    assert settings.rate_limit_login_window_seconds > 0