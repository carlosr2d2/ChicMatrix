from fastapi.testclient import TestClient

from app.models.models import User
from app.services.password import hash_password, verify_password


def test_register_email_success(client: TestClient, db_session):
    response = client.post(
        "/register/email",
        json={
            "email": "newuser@chicmatrix.app",
            "password": "SecurePass123",
            "name": "New User",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@chicmatrix.app"
    assert data["verified"] is False
    assert data["verification_token"] is not None

    user = db_session.query(User).filter(User.email == "newuser@chicmatrix.app").first()
    assert user is not None
    assert user.password_hash is not None
    assert user.consent_version == "1.0"
    assert user.consent_given_at is not None
    assert verify_password("SecurePass123", user.password_hash)


def test_register_requires_consent(client: TestClient):
    response = client.post(
        "/register/email",
        json={
            "email": "noconsent@chicmatrix.app",
            "password": "SecurePass123",
            "consent_accepted": False,
        },
    )
    assert response.status_code == 400
    assert "consent" in response.json()["detail"].lower()


def test_register_duplicate_verified_email(client: TestClient, db_session):
    db_session.add(
        User(
            email="existing@chicmatrix.app",
            password_hash=hash_password("SecurePass123"),
            verified=True,
        )
    )
    db_session.commit()

    response = client.post(
        "/register/email",
        json={
            "email": "existing@chicmatrix.app",
            "password": "AnotherPass123",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 409


def test_register_weak_password_rejected(client: TestClient):
    response = client.post(
        "/register/email",
        json={
            "email": "weak@chicmatrix.app",
            "password": "short",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 422


def test_verify_email_success(client: TestClient):
    register = client.post(
        "/register/email",
        json={
            "email": "verifyme@chicmatrix.app",
            "password": "SecurePass123",
            "consent_accepted": True,
        },
    )
    token = register.json()["verification_token"]

    response = client.post("/verify/email", json={"token": token})
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["email"] == "verifyme@chicmatrix.app"


def test_verify_email_invalid_token(client: TestClient):
    response = client.post("/verify/email", json={"token": "invalid-token-value"})
    assert response.status_code == 400


def test_verify_email_token_single_use(client: TestClient):
    register = client.post(
        "/register/email",
        json={
            "email": "once@chicmatrix.app",
            "password": "SecurePass123",
            "consent_accepted": True,
        },
    )
    token = register.json()["verification_token"]

    first = client.post("/verify/email", json={"token": token})
    assert first.status_code == 200

    second = client.post("/verify/email", json={"token": token})
    assert second.status_code == 400
