from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BrandProfileBase(BaseModel):
    name: str = "Default Brand"
    voice_description: str = ""
    primary_color: str = "#1F6F5C"
    secondary_color: str = "#3AAFA9"
    font_family: str = "Inter, sans-serif"
    tone_keywords: str = ""
    is_active: bool = True


class BrandProfileCreate(BrandProfileBase):
    pass


class BrandProfileUpdate(BaseModel):
    name: Optional[str] = None
    voice_description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    font_family: Optional[str] = None
    tone_keywords: Optional[str] = None
    is_active: Optional[bool] = None


class BrandProfileOut(BrandProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
