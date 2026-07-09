import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.models import User
from app.schemas.auth import (
    EmailRegisterRequest,
    EmailRegisterResponse,
    PhoneRegisterRequest,
    PhoneRegisterResponse,
)
from app.services.email_verification import EmailVerificationService
from app.services.password import hash_password
from app.services.phone_verification import PhoneVerificationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/register", tags=["auth"])


@router.post("/email", response_model=EmailRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_with_email(payload: EmailRegisterRequest, db: Session = Depends(get_db)):
    if not payload.consent_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit consent is required to process your personal data (GDPR/Habeas Data)",
        )

    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        if existing.verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email pending verification. Check your inbox or request a new link.",
        )

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        name=payload.name,
        verified=False,
        consent_given_at=datetime.now(timezone.utc),
        consent_version=settings.consent_version,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    verification_service = EmailVerificationService(db)
    raw_token = verification_service.create_token(user)
    verification_service.send_verification_email(user, raw_token)

    logger.info("User registered via email", extra={"user_id": str(user.id), "email": user.email})

    debug_token = raw_token if settings.email_debug and not settings.smtp_host else None

    return EmailRegisterResponse(
        user_id=user.id,
        email=user.email,
        verified=user.verified,
        message="Registration successful. Please verify your email.",
        verification_token=debug_token,
    )


@router.post("/phone", response_model=PhoneRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_with_phone(payload: PhoneRegisterRequest, db: Session = Depends(get_db)):
    if not payload.consent_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Explicit consent is required to process your personal data (GDPR/Habeas Data)",
        )

    phone_service = PhoneVerificationService(db)
    try:
        phone = phone_service.normalize_phone(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        if existing.verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered",
            )
        user = existing
        if payload.name:
            user.name = payload.name
        user.consent_given_at = datetime.now(timezone.utc)
        user.consent_version = settings.consent_version
    else:
        user = User(
            phone=phone,
            name=payload.name,
            verified=False,
            consent_given_at=datetime.now(timezone.utc),
            consent_version=settings.consent_version,
        )
        db.add(user)

    db.commit()
    db.refresh(user)

    otp_code = phone_service.create_otp(user)
    phone_service.send_otp_sms(phone, otp_code)

    logger.info("User registered via phone", extra={"user_id": str(user.id), "phone": phone})

    debug_otp = otp_code if settings.sms_debug and not settings.twilio_account_sid else None

    return PhoneRegisterResponse(
        user_id=user.id,
        phone=phone,
        verified=user.verified,
        message="OTP sent to your phone. Please verify to complete registration.",
        otp_code=debug_otp,
    )
