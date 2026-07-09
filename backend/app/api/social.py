import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import SocialAuthRequest, SocialAuthResponse
from app.services.oauth_providers import OAuthProviderError
from app.services.phone_verification import PhoneVerificationService
from app.services.social_auth import SocialAuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/social", response_model=SocialAuthResponse)
def social_login(payload: SocialAuthRequest, db: Session = Depends(get_db)):
    phone = None
    if payload.phone:
        phone_service = PhoneVerificationService(db)
        try:
            phone = phone_service.normalize_phone(payload.phone)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    service = SocialAuthService(db)
    try:
        user, linked_existing, message = service.authenticate(
            provider=payload.provider,
            id_token=payload.id_token,
            consent_accepted=payload.consent_accepted,
            name=payload.name,
            phone=phone,
        )
    except OAuthProviderError as exc:
        detail = str(exc)
        status_code = status.HTTP_400_BAD_REQUEST
        if "consent" in detail.lower():
            status_code = status.HTTP_400_BAD_REQUEST
        elif "already linked" in detail.lower():
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=detail) from exc

    logger.info(
        "Social login completed",
        extra={
            "user_id": str(user.id),
            "provider": payload.provider,
            "linked_existing": linked_existing,
        },
    )

    return SocialAuthResponse(
        user_id=user.id,
        email=user.email,
        phone=user.phone,
        verified=user.verified,
        social_provider=user.social_provider,
        linked_existing_account=linked_existing,
        message=message,
    )
