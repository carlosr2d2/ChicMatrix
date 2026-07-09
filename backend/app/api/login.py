import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.permissions import permissions_for_role
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    PhoneOtpLoginResponse,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user
from app.models.models import User
from app.services.jwt_tokens import JwtTokenService, TokenError
from app.services.login import LoginError, LoginService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


def _client_meta(request: Request) -> tuple[str | None, str | None]:
    user_agent = request.headers.get("user-agent")
    forwarded = request.headers.get("x-forwarded-for")
    ip_address = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
    return user_agent, ip_address


def _token_response(user, access_token: str, refresh_token: str) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
        user_id=user.id,
        role=user.role,
        permissions=permissions_for_role(user.role),
    )


@router.post("/login", response_model=TokenResponse | PhoneOtpLoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    service = LoginService(db)
    user_agent, ip_address = _client_meta(request)

    if payload.method == "email":
        if not payload.email or not payload.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email and password are required for email login",
            )
        try:
            user = service.login_with_email(payload.email, payload.password)
        except LoginError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        access_token, refresh_token = service.issue_tokens(
            user, user_agent=user_agent, ip_address=ip_address
        )
        logger.info("User logged in via email", extra={"user_id": str(user.id)})
        return _token_response(user, access_token, refresh_token)

    if payload.method == "phone":
        if not payload.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="phone is required for phone login",
            )
        if not payload.otp_code:
            try:
                _, otp_code = service.request_phone_otp(payload.phone)
            except LoginError as exc:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

            debug_otp = otp_code if settings.sms_debug and not settings.twilio_account_sid else None
            return PhoneOtpLoginResponse(
                message="OTP sent to your phone. Submit the same request with otp_code to complete login.",
                otp_code=debug_otp,
            )

        try:
            user = service.login_with_phone(payload.phone, payload.otp_code)
        except LoginError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        access_token, refresh_token = service.issue_tokens(
            user, user_agent=user_agent, ip_address=ip_address
        )
        logger.info("User logged in via phone", extra={"user_id": str(user.id)})
        return _token_response(user, access_token, refresh_token)

    if payload.method == "social":
        if not payload.provider or not payload.id_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="provider and id_token are required for social login",
            )
        try:
            user = service.login_with_social(payload.provider, payload.id_token)
        except LoginError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

        access_token, refresh_token = service.issue_tokens(
            user, user_agent=user_agent, ip_address=ip_address
        )
        logger.info(
            "User logged in via social",
            extra={"user_id": str(user.id), "provider": payload.provider},
        )
        return _token_response(user, access_token, refresh_token)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported login method")


@router.post("/login/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    token_service = JwtTokenService(db)
    user_agent, ip_address = _client_meta(request)

    try:
        access_token, refresh_token, user = token_service.rotate_refresh_token(
            payload.refresh_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    logger.info("Tokens refreshed", extra={"user_id": str(user.id)})
    return _token_response(user, access_token, refresh_token)


@router.post("/login/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token_service = JwtTokenService(db)
    try:
        session = token_service.validate_refresh_token(payload.refresh_token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token_service.revoke_session(session)
    logger.info("User logged out", extra={"user_id": str(session.user_id)})


@router.get("/auth/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    return user
