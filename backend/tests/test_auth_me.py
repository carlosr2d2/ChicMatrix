from fastapi.testclient import TestClient

from app.models.enums import UserRole
from app.models.models import User
from app.services.password import hash_password


def test_get_me_with_valid_token(client: TestClient, db_session):
    user = User(
        email="me@chicmatrix.app",
        password_hash=hash_password("SecurePass123"),
        name="Me User",
        verified=True,
        role=UserRole.USER.value,
    )
    db_session.add(user)
    db_session.commit()

    login = client.post(
        "/login",
        json={
            "method": "email",
            "email": "me@chicmatrix.app",
            "password": "SecurePass123",
        },
    )
    assert login.status_code == 200
    access_token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@chicmatrix.app"
    assert data["name"] == "Me User"
    assert data["role"] == "user"
    assert data["verified"] is True


def test_get_me_without_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_me_with_invalid_token(client: TestClient):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
