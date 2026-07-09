import pytest

from app.services.oauth_providers import GoogleTokenVerifier, OAuthProviderError
from app.services.social_auth import SocialAuthService
from app.services.social_profile import SocialProfile


def test_google_debug_token_parsing():
    profile = GoogleTokenVerifier().verify(
        "debug-google:google-debug-1:test@example.com:Test Name"
    )
    assert profile.social_id == "google-debug-1"
    assert profile.email == "test@example.com"
    assert profile.name == "Test Name"
    assert profile.provider == "google"


def test_social_auth_service_conflict_on_different_social(db_session):
    from app.models.models import User

    db_session.add(
        User(
            email="conflict@chicmatrix.app",
            social_provider="google",
            social_id="existing-google-id",
            verified=True,
        )
    )
    db_session.commit()

    mock = type("MockVerifier", (), {})()

    def verify(provider, id_token):
        return SocialProfile(
            provider="apple",
            social_id="new-apple-id",
            email="conflict@chicmatrix.app",
        )

    mock.verify = verify
    service = SocialAuthService(db_session, verifier=mock)

    with pytest.raises(OAuthProviderError, match="already linked"):
        service.authenticate(
            provider="apple",
            id_token="token",
            consent_accepted=True,
        )
