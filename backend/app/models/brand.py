from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, default="Default Brand")
    voice_description: Mapped[str] = mapped_column(Text, default="")
    primary_color: Mapped[str] = mapped_column(String, default="#1F6F5C")
    secondary_color: Mapped[str] = mapped_column(String, default="#3AAFA9")
    font_family: Mapped[str] = mapped_column(String, default="Inter, sans-serif")
    tone_keywords: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
