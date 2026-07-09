from fastapi.testclient import TestClient

from app.models.models import User
from app.services.password import hash_password


def test_register_phone_success(client: TestClient, db_session):
    response = client.post(
        "/register/phone",
        json={
            "phone": "+573001112233",
            "name": "Phone User",
            "consent_accepted": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "+573001112233"
    assert data["verified"] is False
    assert data["otp_code"] is not None
    assert len(data["otp_code"]) == 6

    user = db_session.query(User).filter(User.phone == "+573001112233").first()
    assert user is not None
    assert user.otp_secret is not None
    assert user.consent_version == "1.0"


def test_register_phone_requires_consent(client: TestClient):
    response = client.post(
        "/register/phone",
        json={"phone": "+573009998877", "consent_accepted": False},
    )
    assert response.status_code == 400


def test_register_phone_invalid_format(client: TestClient):
    response = client.post(
        "/register/phone",
        json={"phone": "3001112233", "consent_accepted": True},
    )
    assert response.status_code == 422


def test_register_phone_duplicate_verified(client: TestClient, db_session):
    db_session.add(User(phone="+573005554433", verified=True))
    db_session.commit()

    response = client.post(
        "/register/phone",
        json={"phone": "+573005554433", "consent_accepted": True},
    )
    assert response.status_code == 409


def test_register_phone_resends_otp_for_unverified(client: TestClient):
    first = client.post(
        "/register/phone",
        json={"phone": "+573004445566", "consent_accepted": True},
    )
    second = client.post(
        "/register/phone",
        json={"phone": "+573004445566", "consent_accepted": True},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["user_id"] == second.json()["user_id"]


def test_verify_phone_success(client: TestClient):
    register = client.post(
        "/register/phone",
        json={"phone": "+573007778899", "consent_accepted": True},
    )
    otp = register.json()["otp_code"]

    response = client.post(
        "/verify/phone",
        json={"phone": "+573007778899", "otp_code": otp},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["phone"] == "+573007778899"


def test_verify_phone_invalid_otp(client: TestClient):
    client.post(
        "/register/phone",
        json={"phone": "+573006667788", "consent_accepted": True},
    )
    response = client.post(
        "/verify/phone",
        json={"phone": "+573006667788", "otp_code": "000000"},
    )
    assert response.status_code == 400


def test_verify_phone_single_use(client: TestClient):
    register = client.post(
        "/register/phone",
        json={"phone": "+573003332211", "consent_accepted": True},
    )
    otp = register.json()["otp_code"]

    first = client.post(
        "/verify/phone",
        json={"phone": "+573003332211", "otp_code": otp},
    )
    assert first.status_code == 200

    second = client.post(
        "/verify/phone",
        json={"phone": "+573003332211", "otp_code": otp},
    )
    assert second.status_code == 400
