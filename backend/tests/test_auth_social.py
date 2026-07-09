from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.models.models import User
from app.services.password import hash_password
from app.services.social_auth import SocialAuthService
from app.services.social_profile import SocialProfile


@pytest.fixture()
def mock_verifier():
    verifier = MagicMock()

    def verify(provider: str, id_token: str) -> SocialProfile:
        if id_token == "google-token-new":
            return SocialProfile(
                provider="google",
                social_id="google-user-001",
                email="social.new@chicmatrix.app",
                name="Google User",
            )
        if id_token == "google-token-link":
            return SocialProfile(
                provider="google",
                social_id="google-user-002",
                email="existing@chicmatrix.app",
                name="Google Link",
            )
        if id_token == "apple-token-new":
            return SocialProfile(
                provider="apple",
                social_id="apple-user-001",
                email="apple.new@chicmatrix.app",
            )
        if id_token == "google-token-returning":
            return SocialProfile(
                provider="google",
                social_id="google-user-returning",
                email="returning@chicmatrix.app",
                name="Returning User",
            )
        if id_token == "google-token-phone-link":
            return SocialProfile(
                provider="google",
                social_id="google-user-phone-link",
                email=None,
                name="Phone Link",
            )
        raise ValueError("Unknown test token")

    verifier.verify.side_effect = verify
    return verifier


@pytest.fixture()
def social_client(client: TestClient, mock_verifier, monkeypatch):
    monkeypatch.setattr(
        "app.api.social.SocialAuthService",
        lambda db: SocialAuthService(db, verifier=mock_verifier),
    )
    yield client


def test_social_login_creates_new_google_user(social_client: TestClient, db_session):
    response = social_client.post(
        "/auth/social",
        json={
            "provider": "google",
            "id_token": "google-token-new",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["social_provider"] == "google"
    assert data["verified"] is True
    assert data["linked_existing_account"] is False
    assert data["email"] == "social.new@chicmatrix.app"

    user = db_session.query(User).filter(User.email == "social.new@chicmatrix.app").first()
    assert user.social_id == "google-user-001"


def test_social_login_requires_consent_for_new_user(social_client: TestClient):
    response = social_client.post(
        "/auth/social",
        json={
            "provider": "apple",
            "id_token": "apple-token-new",
            "consent_accepted": False,
        },
    )
    assert response.status_code == 400
    assert "consent" in response.json()["detail"].lower()


def test_social_login_links_existing_email_account(social_client: TestClient, db_session):
    db_session.add(
        User(
            email="existing@chicmatrix.app",
            password_hash=hash_password("SecurePass123"),
            verified=True,
        )
    )
    db_session.commit()

    response = social_client.post(
        "/auth/social",
        json={
            "provider": "google",
            "id_token": "google-token-link",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["linked_existing_account"] is True
    assert data["email"] == "existing@chicmatrix.app"

    user = db_session.query(User).filter(User.email == "existing@chicmatrix.app").first()
    assert user.social_provider == "google"
    assert user.social_id == "google-user-002"


def test_social_login_links_existing_phone_account(social_client: TestClient, db_session):
    db_session.add(User(phone="+573008889900", verified=True))
    db_session.commit()

    response = social_client.post(
        "/auth/social",
        json={
            "provider": "google",
            "id_token": "google-token-phone-link",
            "phone": "+573008889900",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["linked_existing_account"] is True
    assert data["phone"] == "+573008889900"

    user = db_session.query(User).filter(User.phone == "+573008889900").first()
    assert user.social_provider == "google"
    assert user.social_id == "google-user-phone-link"


def test_social_login_returning_user(social_client: TestClient, db_session):
    db_session.add(
        User(
            email="returning@chicmatrix.app",
            social_provider="google",
            social_id="google-user-returning",
            verified=True,
        )
    )
    db_session.commit()

    response = social_client.post(
        "/auth/social",
        json={
            "provider": "google",
            "id_token": "google-token-returning",
            "consent_accepted": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["linked_existing_account"] is False
    assert data["email"] == "returning@chicmatrix.app"


def test_social_login_debug_token_integration(client: TestClient, db_session):
    response = client.post(
        "/auth/social",
        json={
            "provider": "google",
            "id_token": "debug-google:debug-user-01:debug@chicmatrix.app:Debug User",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "debug@chicmatrix.app"
    assert data["social_provider"] == "google"


def test_social_login_invalid_provider(client: TestClient):
    response = client.post(
        "/auth/social",
        json={
            "provider": "facebook",
            "id_token": "some-token-value",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 422
