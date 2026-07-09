import logging

from sqlalchemy.orm import Session

from app.models.models import User
from app.services.jwt_tokens import JwtTokenService
from app.services.oauth_providers import OAuthProviderError
from app.services.password import verify_password
from app.services.phone_verification import PhoneVerificationService
from app.services.social_auth import SocialAuthService

logger = logging.getLogger(__name__)


class LoginError(Exception):
    pass


class LoginService:
    def __init__(self, db: Session, social_service: SocialAuthService | None = None):
        self.db = db
        self.tokens = JwtTokenService(db)
        self.phone = PhoneVerificationService(db)
        self.social = social_service or SocialAuthService(db)

    def login_with_email(self, email: str, password: str) -> User:
        user = self.db.query(User).filter(User.email == email.lower()).first()
        if not user or not user.password_hash:
            raise LoginError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise LoginError("Invalid email or password")
        if not user.verified:
            raise LoginError("Email not verified. Please check your inbox.")
        return user

    def request_phone_otp(self, phone: str) -> tuple[User, str | None]:
        try:
            user, otp_code = self.phone.request_login_otp(phone)
        except ValueError as exc:
            raise LoginError(str(exc)) from exc
        return user, otp_code

    def login_with_phone(self, phone: str, otp_code: str) -> User:
        try:
            user = self.phone.verify_otp(phone, otp_code)
        except ValueError as exc:
            raise LoginError(str(exc)) from exc
        return user

    def login_with_social(self, provider: str, id_token: str) -> User:
        try:
            return self.social.login_existing(provider, id_token)
        except OAuthProviderError as exc:
            raise LoginError(str(exc)) from exc

    def issue_tokens(
        self,
        user: User,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[str, str]:
        return self.tokens.issue_token_pair(user, user_agent=user_agent, ip_address=ip_address)
