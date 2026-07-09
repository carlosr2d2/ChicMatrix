from unittest.mock import MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.models.enums import UserRole
from app.models.models import Session, User
from app.permissions import permissions_for_role
from app.services.password import hash_password
from app.services.social_auth import SocialAuthService
from app.services.social_profile import SocialProfile


@pytest.fixture()
def verified_email_user(db_session):
    user = User(
        email="login@chicmatrix.app",
        password_hash=hash_password("SecurePass123"),
        name="Login User",
        verified=True,
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def verified_phone_user(db_session):
    user = User(
        phone="+573001234567",
        name="Phone Login",
        verified=True,
        otp_secret="test-secret",
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def social_user(db_session):
    user = User(
        email="social.login@chicmatrix.app",
        social_provider="google",
        social_id="google-login-001",
        verified=True,
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def mock_social_verifier():
    verifier = MagicMock()

    def verify(provider: str, id_token: str) -> SocialProfile:
        if id_token == "google-login-token":
            return SocialProfile(
                provider="google",
                social_id="google-login-001",
                email="social.login@chicmatrix.app",
            )
        if id_token == "google-unknown-token":
            return SocialProfile(
                provider="google",
                social_id="google-unknown-999",
                email="unknown@chicmatrix.app",
            )
        raise ValueError("Unknown token")

    verifier.verify.side_effect = verify
    return verifier


@pytest.fixture()
def login_client(client: TestClient, mock_social_verifier, monkeypatch):
    monkeypatch.setattr(
        "app.api.login.LoginService",
        lambda db: __import__("app.services.login", fromlist=["LoginService"]).LoginService(
            db, social_service=SocialAuthService(db, verifier=mock_social_verifier)
        ),
    )
    yield client


def test_login_email_success(login_client: TestClient, verified_email_user):
    response = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user_id"] == str(verified_email_user.id)
    assert data["role"] == "user"
    assert "read:recommendations" in data["permissions"]
    assert data["access_token"]
    assert data["refresh_token"]

    payload = jwt.decode(
        data["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == str(verified_email_user.id)
    assert payload["role"] == "user"
    assert payload["type"] == "access"
    assert payload["permissions"] == permissions_for_role("user")


def test_login_email_invalid_password(login_client: TestClient, verified_email_user):
    response = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "WrongPass123",
        },
    )
    assert response.status_code == 401


def test_login_email_unverified(login_client: TestClient, db_session):
    db_session.add(
        User(
            email="unverified@chicmatrix.app",
            password_hash=hash_password("SecurePass123"),
            verified=False,
        )
    )
    db_session.commit()

    response = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "unverified@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    assert response.status_code == 401
    assert "verified" in response.json()["detail"].lower()


def test_login_phone_request_otp(login_client: TestClient, verified_phone_user):
    response = login_client.post(
        "/login",
        json={"method": "phone", "phone": "+573001234567"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "OTP sent" in data["message"]
    assert data["otp_code"] is not None


def test_login_phone_with_otp(login_client: TestClient, verified_phone_user):
    otp_response = login_client.post(
        "/login",
        json={"method": "phone", "phone": "+573001234567"},
    )
    otp = otp_response.json()["otp_code"]

    response = login_client.post(
        "/login",
        json={"method": "phone", "phone": "+573001234567", "otp_code": otp},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_login_social_success(login_client: TestClient, social_user):
    response = login_client.post(
        "/login",
        json={
            "method": "social",
            "provider": "google",
            "id_token": "google-login-token",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(social_user.id)


def test_login_social_account_not_found(login_client: TestClient):
    response = login_client.post(
        "/login",
        json={
            "method": "social",
            "provider": "google",
            "id_token": "google-unknown-token",
        },
    )
    assert response.status_code == 401
    assert "not found" in response.json()["detail"].lower()


def test_refresh_tokens(login_client: TestClient, verified_email_user):
    login = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    refresh_token = login.json()["refresh_token"]

    response = login_client.post("/login/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"] != refresh_token


def test_refresh_token_single_use_rotation(login_client: TestClient, verified_email_user):
    login = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    old_refresh = login.json()["refresh_token"]

    login_client.post("/login/refresh", json={"refresh_token": old_refresh})

    second = login_client.post("/login/refresh", json={"refresh_token": old_refresh})
    assert second.status_code == 401


def test_logout_revokes_refresh_token(login_client: TestClient, verified_email_user):
    login = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    refresh_token = login.json()["refresh_token"]

    logout = login_client.post("/login/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 204

    refresh = login_client.post("/login/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 401


def test_admin_role_permissions(db_session, login_client: TestClient):
    user = User(
        email="admin@chicmatrix.app",
        password_hash=hash_password("SecurePass123"),
        verified=True,
        role=UserRole.ADMIN.value,
    )
    db_session.add(user)
    db_session.commit()

    response = login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "admin@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    assert response.status_code == 200
    permissions = response.json()["permissions"]
    assert "admin:users" in permissions
    assert response.json()["role"] == "admin"


def test_session_stored_in_database(login_client: TestClient, verified_email_user, db_session):
    login_client.post(
        "/login",
        json={
            "method": "email",
            "email": "login@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    sessions = db_session.query(Session).filter(Session.user_id == verified_email_user.id).all()
    assert len(sessions) == 1
    assert sessions[0].refresh_token_hash
    assert sessions[0].revoked_at is None
