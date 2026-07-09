from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserAuthBase(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=r"^\+[1-9]\d{6,14}$")
    verified: bool = False
    social_provider: str | None = None
    social_id: str | None = None


class UserProfileBase(BaseModel):
    name: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    body_proportions: dict | None = None
    preferences: dict | None = None
    habits: dict | None = None


class UserResponse(UserAuthBase, UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    consent_given_at: datetime | None = None
    consent_version: str | None = None
    created_at: datetime
    updated_at: datetime
