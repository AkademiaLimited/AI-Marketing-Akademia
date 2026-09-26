from app.core.providers.base import AbstractProvider
from app.core.providers.mock_provider import MockProvider

__all__ = ["AbstractProvider", "MockProvider", "get_provider"]


def get_provider(platform: str, require_real: bool = False) -> AbstractProvider:
    """Factory: return a provider instance for the given platform.

    Currently always returns a MockProvider since real social API
    integrations are not yet implemented. When API credentials are
    configured, this would return a real provider implementation.

    Args:
        platform: Platform name (instagram, linkedin, twitter, email, etc.)
        require_real: If True, raise when no real provider is available.
    """
    if require_real:
        raise NotImplementedError(f"Real {platform} provider not yet implemented")
    return MockProvider(platform)
