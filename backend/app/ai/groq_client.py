import json
from typing import Any, Optional

from groq import AsyncGroq

from app.core.config import settings

_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


async def call_groq(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    brand_context: Optional[str] = None,
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """Call Groq for a text completion.

    Args:
        prompt: The user prompt.
        system_prompt: The base system prompt.
        brand_context: Optional brand identity context, prepended to system_prompt.
    """
    full_system = system_prompt
    if brand_context:
        full_system = f"{brand_context}\n{full_system}"

    client = get_client()
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


async def call_groq_json(
    prompt: str,
    system_prompt: str = "You are a helpful assistant. Return valid JSON only.",
    brand_context: Optional[str] = None,
    model: str = "openai/gpt-oss-120b",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    """Call Groq for a JSON completion.

    Args:
        prompt: The user prompt.
        system_prompt: The base system prompt.
        brand_context: Optional brand identity context, prepended to system_prompt.
    """
    full_system = system_prompt
    if brand_context:
        full_system = f"{brand_context}\n{full_system}"

    client = get_client()
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    if raw is None:
        raise ValueError("No content returned from Groq")
    return json.loads(raw)
