from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

PHONE_PATTERN = r"^\+[1-9]\d{6,14}$"


class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=120)
    consent_accepted: bool = Field(
        description="Explicit GDPR/Habeas Data consent required to register"
    )


class EmailRegisterResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    verified: bool
    message: str
    verification_token: str | None = Field(
        default=None,
        description="Only returned in debug mode when SMTP is not configured",
    )


class EmailVerifyRequest(BaseModel):
    token: str = Field(min_length=10)


class EmailVerifyResponse(BaseModel):
    user_id: UUID
    email: EmailStr | None
    verified: bool
    message: str


class PhoneRegisterRequest(BaseModel):
    phone: str = Field(pattern=PHONE_PATTERN, examples=["+573001234567"])
    name: str | None = Field(default=None, max_length=120)
    consent_accepted: bool = Field(
        description="Explicit GDPR/Habeas Data consent required to register"
    )


class PhoneRegisterResponse(BaseModel):
    user_id: UUID
    phone: str
    verified: bool
    message: str
    otp_code: str | None = Field(
        default=None,
        description="Only returned in debug mode when Twilio is not configured",
    )


class PhoneVerifyRequest(BaseModel):
    phone: str = Field(pattern=PHONE_PATTERN, examples=["+573001234567"])
    otp_code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class PhoneVerifyResponse(BaseModel):
    user_id: UUID
    phone: str | None
    verified: bool
    message: str


class SocialAuthRequest(BaseModel):
    provider: str = Field(pattern="^(google|apple)$")
    id_token: str = Field(min_length=10)
    name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    consent_accepted: bool = Field(
        default=False,
        description="Required when creating a new account",
    )


class SocialAuthResponse(BaseModel):
    user_id: UUID
    email: EmailStr | None = None
    phone: str | None = None
    verified: bool
    social_provider: str
    linked_existing_account: bool
    message: str


class LoginRequest(BaseModel):
    method: str = Field(pattern="^(email|phone|social)$")
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    otp_code: str | None = Field(default=None, min_length=6, max_length=6, pattern=r"^\d{6}$")
    provider: str | None = Field(default=None, pattern="^(google|apple)$")
    id_token: str | None = Field(default=None, min_length=10)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token lifetime in seconds")
    user_id: UUID
    role: str
    permissions: list[str]


class PhoneOtpLoginResponse(BaseModel):
    message: str
    otp_code: str | None = Field(
        default=None,
        description="Only returned in debug mode when Twilio is not configured",
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=10)
