from typing import Any

from pydantic import BaseModel


class PostResponse(BaseModel):
    post_id: str
    platform: str
    status: str  # published, scheduled, failed, processing
    permalink: str | None = None
    provider_message: str | None = None
    raw: dict[str, Any] = {}


class EngagementResponse(BaseModel):
    post_id: str
    platform: str
    impressions: int = 0
    engagements: int = 0
    clicks: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    saved: int = 0
    raw: dict[str, Any] = {}


class MessageResponse(BaseModel):
    message_id: str
    platform: str
    sender: str
    content: str
    direction: str  # incoming, outgoing
    timestamp: str
    thread_id: str | None = None
    raw: dict[str, Any] = {}
