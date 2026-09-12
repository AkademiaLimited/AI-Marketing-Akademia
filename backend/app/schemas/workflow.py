from pydantic import BaseModel, ConfigDict


class WorkflowRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_type: str
    status: str
    lead_id: str
    error: str
    started_at: str
    finished_at: str


class MarketingActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workflow_run_id: str
    lead_id: str
    email_id: str
    activity_type: str
    channel: str
    source_url: str
    status: str
    provider_message_id: str
    details: str
    error: str
    created_at: str