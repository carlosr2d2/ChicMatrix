import logging

import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings
from app.models.enums import SocialProvider
from app.services.social_profile import SocialProfile

logger = logging.getLogger(__name__)

APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class OAuthProviderError(ValueError):
    pass


class GoogleTokenVerifier:
    def verify(self, id_token: str) -> SocialProfile:
        if settings.social_auth_debug and id_token.startswith("debug-google:"):
            return self._parse_debug_token(id_token, SocialProvider.GOOGLE.value)

        if not settings.google_client_id:
            raise OAuthProviderError("Google client ID is not configured")

        with httpx.Client(timeout=10.0) as client:
            response = client.get(GOOGLE_TOKENINFO_URL, params={"id_token": id_token})

        if response.status_code != 200:
            raise OAuthProviderError("Invalid Google ID token")

        data = response.json()
        audience = data.get("aud") or data.get("azp")
        if audience != settings.google_client_id:
            raise OAuthProviderError("Google token audience mismatch")

        email_verified = str(data.get("email_verified", "false")).lower() == "true"
        return SocialProfile(
            provider=SocialProvider.GOOGLE.value,
            social_id=data["sub"],
            email=data.get("email"),
            name=data.get("name"),
            email_verified=email_verified,
        )


class AppleTokenVerifier:
    def verify(self, id_token: str) -> SocialProfile:
        if settings.social_auth_debug and id_token.startswith("debug-apple:"):
            return self._parse_debug_token(id_token, SocialProvider.APPLE.value)

        if not settings.apple_client_id:
            raise OAuthProviderError("Apple client ID is not configured")

        jwks_client = PyJWKClient(APPLE_JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.apple_client_id,
            issuer="https://appleid.apple.com",
        )

        return SocialProfile(
            provider=SocialProvider.APPLE.value,
            social_id=payload["sub"],
            email=payload.get("email"),
            name=None,
            email_verified=str(payload.get("email_verified", "true")).lower() == "true",
        )


def _parse_debug_token(id_token: str, provider: str) -> SocialProfile:
    # Format: debug-google:sub:email[:name] or debug-apple:sub:email
    parts = id_token.split(":", 3)
    if len(parts) < 3:
        raise OAuthProviderError("Invalid debug social token format")

    social_id = parts[1]
    email = parts[2] if parts[2] else None
    name = parts[3] if len(parts) > 3 and parts[3] else None
    return SocialProfile(
        provider=provider,
        social_id=social_id,
        email=email,
        name=name,
        email_verified=True,
    )


GoogleTokenVerifier._parse_debug_token = staticmethod(_parse_debug_token)
AppleTokenVerifier._parse_debug_token = staticmethod(_parse_debug_token)


class SocialTokenVerifier:
    def __init__(self):
        self._google = GoogleTokenVerifier()
        self._apple = AppleTokenVerifier()

    def verify(self, provider: str, id_token: str) -> SocialProfile:
        if provider == SocialProvider.GOOGLE.value:
            return self._google.verify(id_token)
        if provider == SocialProvider.APPLE.value:
            return self._apple.verify(id_token)
        raise OAuthProviderError(f"Unsupported provider: {provider}")
