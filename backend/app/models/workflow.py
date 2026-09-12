from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="running")
    lead_id: Mapped[str] = mapped_column(String, default="")
    error: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[str] = mapped_column(String, default="")
    finished_at: Mapped[str] = mapped_column(String, default="")


class MarketingActivity(Base):
    __tablename__ = "marketing_activities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workflow_run_id: Mapped[str] = mapped_column(String, nullable=False)
    lead_id: Mapped[str] = mapped_column(String, default="")
    email_id: Mapped[str] = mapped_column(String, default="")
    activity_type: Mapped[str] = mapped_column(String, nullable=False)
    channel: Mapped[str] = mapped_column(String, default="")
    source_url: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="completed")
    provider_message_id: Mapped[str] = mapped_column(String, default="")
    details: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String, default="")