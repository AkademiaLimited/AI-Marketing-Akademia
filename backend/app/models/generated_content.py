from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String, nullable=False)
    caption: Mapped[str] = mapped_column(Text, default="")
    hashtags: Mapped[str] = mapped_column(Text, default="")
    call_to_action: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String, default="generated")
    scheduled_at: Mapped[str] = mapped_column(String, default="")
    post_id: Mapped[str] = mapped_column(String, default="")
