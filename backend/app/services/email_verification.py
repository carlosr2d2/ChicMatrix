import hashlib
import logging
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from app.config import settings
from app.models.models import EmailVerificationToken, User

logger = logging.getLogger(__name__)


class EmailVerificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_token(self, user: User) -> str:
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=settings.verification_token_expire_hours
        )

        self.db.add(
            EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )
        self.db.commit()
        return raw_token

    def verify_token(self, raw_token: str) -> User:
        token_hash = self._hash_token(raw_token)
        record = (
            self.db.query(EmailVerificationToken)
            .filter(EmailVerificationToken.token_hash == token_hash)
            .first()
        )
        if not record:
            raise ValueError("Invalid verification token")
        if record.used_at is not None:
            raise ValueError("Verification token already used")
        if self._as_utc(record.expires_at) < datetime.now(timezone.utc):
            raise ValueError("Verification token expired")

        user = self.db.query(User).filter(User.id == record.user_id).first()
        if not user:
            raise ValueError("User not found")

        user.verified = True
        record.used_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    def send_verification_email(self, user: User, raw_token: str) -> None:
        verify_url = f"{settings.frontend_url}/verify-email?token={raw_token}"
        api_url = f"{settings.api_base_url}/verify/email"
        subject = "Verify your ChicMatrix account"
        body = (
            f"Hello,\n\n"
            f"Please verify your email for ChicMatrix.\n\n"
            f"Verification token: {raw_token}\n\n"
            f"Or open this link in your browser:\n{verify_url}\n\n"
            f"You can also verify via API:\nPOST {api_url}\n"
            f'Body: {{"token": "{raw_token}"}}\n\n'
            f"This link expires in {settings.verification_token_expire_hours} hours.\n"
        )

        if settings.smtp_host:
            self._send_smtp(user.email, subject, body)
        else:
            logger.info(
                "Verification email (SMTP not configured)",
                extra={"email": user.email, "verify_url": verify_url, "token": raw_token},
            )

    @staticmethod
    def _hash_token(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _send_smtp(to_email: str | None, subject: str, body: str) -> None:
        if not to_email:
            raise ValueError("User has no email address")

        message = MIMEMultipart()
        message["From"] = settings.email_from
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.email_from, to_email, message.as_string())

        logger.info("Verification email sent", extra={"email": to_email})
