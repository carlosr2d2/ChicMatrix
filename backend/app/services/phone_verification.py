import hashlib
import logging
import re
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import PhoneOtpChallenge, User
from app.services.sms import SmsService

logger = logging.getLogger(__name__)


class PhoneVerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.sms = SmsService()

    def normalize_phone(self, phone: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", phone.strip())
        if not cleaned.startswith("+") or len(cleaned) < 8:
            raise ValueError("Phone must be in E.164 format, e.g. +573001234567")
        return cleaned

    def create_otp(self, user: User) -> str:
        if not user.otp_secret:
            user.otp_secret = secrets.token_hex(16)

        otp_code = f"{secrets.randbelow(1_000_000):06d}"
        otp_hash = self._hash_otp(otp_code, user.otp_secret)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.otp_expire_minutes)

        self.db.query(PhoneOtpChallenge).filter(
            PhoneOtpChallenge.user_id == user.id,
            PhoneOtpChallenge.used_at.is_(None),
        ).delete()

        self.db.add(
            PhoneOtpChallenge(
                user_id=user.id,
                otp_hash=otp_hash,
                expires_at=expires_at,
            )
        )
        self.db.commit()
        return otp_code

    def verify_otp(self, phone: str, otp_code: str) -> User:
        normalized = self.normalize_phone(phone)
        user = self.db.query(User).filter(User.phone == normalized).first()
        if not user:
            raise ValueError("Phone number not registered")
        if not user.otp_secret:
            raise ValueError("No OTP challenge found for this user")

        otp_hash = self._hash_otp(otp_code, user.otp_secret)
        challenge = (
            self.db.query(PhoneOtpChallenge)
            .filter(
                PhoneOtpChallenge.user_id == user.id,
                PhoneOtpChallenge.otp_hash == otp_hash,
            )
            .order_by(PhoneOtpChallenge.created_at.desc())
            .first()
        )
        if not challenge:
            raise ValueError("Invalid OTP code")
        if challenge.used_at is not None:
            raise ValueError("OTP code already used")
        if self._as_utc(challenge.expires_at) < datetime.now(timezone.utc):
            raise ValueError("OTP code expired")

        user.verified = True
        challenge.used_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    def request_login_otp(self, phone: str) -> tuple[User, str]:
        normalized = self.normalize_phone(phone)
        user = self.db.query(User).filter(User.phone == normalized).first()
        if not user:
            raise ValueError("Phone number not registered")
        if not user.verified:
            raise ValueError("Phone number not verified. Complete registration first.")

        otp_code = self.create_otp(user)
        self.send_otp_sms(normalized, otp_code)
        return user, otp_code

    def send_otp_sms(self, phone: str, otp_code: str) -> None:
        message = (
            f"Your ChicMatrix verification code is {otp_code}. "
            f"It expires in {settings.otp_expire_minutes} minutes."
        )
        self.sms.send_sms(phone, message, otp_code=otp_code)

    @staticmethod
    def _hash_otp(otp_code: str, otp_secret: str) -> str:
        payload = f"{otp_code}:{otp_secret}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
