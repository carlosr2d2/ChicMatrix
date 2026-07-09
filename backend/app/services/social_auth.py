import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.enums import SocialProvider
from app.models.models import User
from app.services.oauth_providers import OAuthProviderError, SocialTokenVerifier
from app.services.social_profile import SocialProfile

logger = logging.getLogger(__name__)


class SocialAuthService:
    def __init__(self, db: Session, verifier: SocialTokenVerifier | None = None):
        self.db = db
        self.verifier = verifier or SocialTokenVerifier()

    def authenticate(
        self,
        provider: str,
        id_token: str,
        consent_accepted: bool,
        name: str | None = None,
        phone: str | None = None,
    ) -> tuple[User, bool, str]:
        """
        Returns (user, linked_existing_account, message).
        """
        if provider not in {p.value for p in SocialProvider}:
            raise OAuthProviderError(f"Unsupported provider: {provider}")

        try:
            profile = self.verifier.verify(provider, id_token)
        except OAuthProviderError:
            raise
        except Exception as exc:
            logger.exception("Social token verification failed", extra={"provider": provider})
            raise OAuthProviderError("Could not verify social login token") from exc

        if name:
            profile.name = name

        existing_social = self._find_by_social(profile)
        if existing_social:
            self._update_profile(existing_social, profile)
            self.db.commit()
            self.db.refresh(existing_social)
            return existing_social, False, "Signed in with social account"

        linked_user = self._link_existing_user(profile, phone=phone)
        if linked_user:
            self.db.commit()
            self.db.refresh(linked_user)
            return linked_user, True, "Social login linked to existing account"

        if not consent_accepted:
            raise OAuthProviderError(
                "Explicit consent is required to create a new account (GDPR/Habeas Data)"
            )

        user = self._create_user(profile)
        self.db.commit()
        self.db.refresh(user)
        return user, False, "Social account created successfully"

    def login_existing(self, provider: str, id_token: str) -> User:
        """Authenticate an existing user via social login (no account creation)."""
        if provider not in {p.value for p in SocialProvider}:
            raise OAuthProviderError(f"Unsupported provider: {provider}")

        try:
            profile = self.verifier.verify(provider, id_token)
        except OAuthProviderError:
            raise
        except Exception as exc:
            logger.exception("Social token verification failed", extra={"provider": provider})
            raise OAuthProviderError("Could not verify social login token") from exc

        user = self._find_by_social(profile)
        if user:
            self._update_profile(user, profile)
            self.db.commit()
            self.db.refresh(user)
            return user

        if profile.email:
            user = self.db.query(User).filter(User.email == profile.email.lower()).first()
            if user:
                if user.social_provider and user.social_id:
                    if user.social_provider != profile.provider or user.social_id != profile.social_id:
                        raise OAuthProviderError("Account already linked to a different social identity")
                else:
                    user.social_provider = profile.provider
                    user.social_id = profile.social_id
                self._update_profile(user, profile)
                self.db.commit()
                self.db.refresh(user)
                return user

        raise OAuthProviderError("Account not found. Please register first.")

    def _find_by_social(self, profile: SocialProfile) -> User | None:
        return (
            self.db.query(User)
            .filter(
                User.social_provider == profile.provider,
                User.social_id == profile.social_id,
            )
            .first()
        )

    def _link_existing_user(self, profile: SocialProfile, phone: str | None = None) -> User | None:
        user = None
        if profile.email:
            user = self.db.query(User).filter(User.email == profile.email.lower()).first()
        if not user and phone:
            user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            return None

        if user.social_provider and user.social_id:
            if user.social_provider != profile.provider or user.social_id != profile.social_id:
                raise OAuthProviderError("Account already linked to a different social identity")
            return user

        user.social_provider = profile.provider
        user.social_id = profile.social_id
        if profile.name and not user.name:
            user.name = profile.name
        if profile.email and not user.email:
            user.email = profile.email.lower()
        if profile.email_verified:
            user.verified = True
        if not user.consent_given_at:
            user.consent_given_at = datetime.now(timezone.utc)
            user.consent_version = settings.consent_version
        return user

    def _create_user(self, profile: SocialProfile) -> User:
        user = User(
            email=profile.email.lower() if profile.email else None,
            name=profile.name,
            social_provider=profile.provider,
            social_id=profile.social_id,
            verified=profile.email_verified,
            consent_given_at=datetime.now(timezone.utc),
            consent_version=settings.consent_version,
        )
        self.db.add(user)
        return user

    @staticmethod
    def _update_profile(user: User, profile: SocialProfile) -> None:
        if profile.name and not user.name:
            user.name = profile.name
        if profile.email and not user.email:
            user.email = profile.email.lower()
        if profile.email_verified:
            user.verified = True
