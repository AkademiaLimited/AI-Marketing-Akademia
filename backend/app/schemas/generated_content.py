from pydantic import BaseModel, ConfigDict


class GeneratedContentBase(BaseModel):
    product_id: str
    platform: str
    caption: str = ""
    hashtags: str = ""
    call_to_action: str = ""
    status: str = "generated"
    scheduled_at: str = ""
    post_id: str = ""


class GeneratedContentCreate(GeneratedContentBase):
    id: str


class GeneratedContentOut(GeneratedContentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class GenerateContentRequest(BaseModel):
    """Request to generate AI content for a product."""
    product_id: str


class SchedulePostRequest(BaseModel):
    """Request to schedule a generated content item for future publishing."""
    content_id: str
    when: str  # ISO-8601 datetime


class PublishNowRequest(BaseModel):
    """Request to publish a generated content item immediately."""
    content_id: str
