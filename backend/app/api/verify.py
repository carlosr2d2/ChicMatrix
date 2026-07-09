import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    EmailVerifyRequest,
    EmailVerifyResponse,
    PhoneVerifyRequest,
    PhoneVerifyResponse,
)
from app.services.email_verification import EmailVerificationService
from app.services.phone_verification import PhoneVerificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/verify", tags=["auth"])


@router.post("/email", response_model=EmailVerifyResponse)
def verify_email(payload: EmailVerifyRequest, db: Session = Depends(get_db)):
    service = EmailVerificationService(db)
    try:
        user = service.verify_token(payload.token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info("Email verified", extra={"user_id": str(user.id), "email": user.email})

    return EmailVerifyResponse(
        user_id=user.id,
        email=user.email,
        verified=user.verified,
        message="Email verified successfully",
    )


@router.post("/phone", response_model=PhoneVerifyResponse)
def verify_phone(payload: PhoneVerifyRequest, db: Session = Depends(get_db)):
    service = PhoneVerificationService(db)
    try:
        user = service.verify_otp(payload.phone, payload.otp_code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    logger.info("Phone verified", extra={"user_id": str(user.id), "phone": user.phone})

    return PhoneVerifyResponse(
        user_id=user.id,
        phone=user.phone,
        verified=user.verified,
        message="Phone verified successfully",
    )
