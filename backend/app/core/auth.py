import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory rate limiting store (use Redis in production)
_login_attempts: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> bool:
    """Return True if the request is allowed, False if rate-limited."""
    now = time.monotonic()
    # Remove attempts outside the window
    _login_attempts[key] = [t for t in _login_attempts[key] if now - t < window_seconds]
    if len(_login_attempts[key]) >= max_attempts:
        return False
    _login_attempts[key].append(now)
    return True


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def validate_password(password: str) -> None:
    """Validate password against policy. Raises ValueError if invalid."""
    if len(password) < settings.password_min_length:
        raise ValueError(
            f"Password must be at least {settings.password_min_length} characters"
        )
    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if settings.password_require_lowercase and not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if settings.password_require_digit and not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


def get_rate_limit_key(request: Request | None = None, identifier: str = "") -> str:
    """Generate a rate limit key from request IP or identifier."""
    if request is not None:
        client_host = request.client.host if request.client else "unknown"
        return f"{client_host}:{identifier}"
    return identifier


async def check_login_rate_limit(request: Request) -> None:
    """Dependency to check login rate limiting."""
    if not settings.rate_limit_enabled:
        return
    key = get_rate_limit_key(request, "login")
    if not _check_rate_limit(
        key,
        settings.rate_limit_login_attempts,
        settings.rate_limit_login_window_seconds,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )