from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import SexCode

ALLOWED_SEX = {c.value for c in SexCode}


class UserAuthBase(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=r"^\+[1-9]\d{6,14}$")
    verified: bool = False
    social_provider: str | None = None
    social_id: str | None = None


class UserProfileBase(BaseModel):
    name: str | None = None
    age: int | None = None
    sex: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    body_proportions: dict | None = None
    preferences: dict | None = None
    habits: dict | None = None


class UserProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=13, le=120)
    sex: str | None = None
    height_cm: float | None = Field(default=None, ge=100, le=250)
    weight_kg: float | None = Field(default=None, ge=30, le=300)
    body_proportions: dict | None = None
    preferences: dict | None = None
    habits: dict | None = None

    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        normalized = value.strip().lower()
        if normalized not in ALLOWED_SEX:
            raise ValueError(f"sex must be one of: {', '.join(sorted(ALLOWED_SEX))}")
        return normalized


class UserResponse(UserAuthBase, UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str = "user"
    consent_given_at: datetime | None = None
    consent_version: str | None = None
    created_at: datetime
    updated_at: datetime
