from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.models.enums import UserRole
from app.models.models import Retailer, User
from app.services.password import hash_password


def _admin_headers(client: TestClient, db_session) -> dict:
    email = "admin.scrape@chicmatrix.app"
    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password("SecurePass123"),
            verified=True,
            role=UserRole.ADMIN.value,
        )
        db_session.add(user)
        db_session.commit()

    login = client.post(
        "/login",
        json={"method": "email", "email": email, "password": "SecurePass123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _user_headers(client: TestClient, db_session) -> dict:
    email = "user.scrape@chicmatrix.app"
    user = db_session.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash=hash_password("SecurePass123"),
            verified=True,
            role=UserRole.USER.value,
        )
        db_session.add(user)
        db_session.commit()

    login = client.post(
        "/login",
        json={"method": "email", "email": email, "password": "SecurePass123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_enqueue_scrape_success(client: TestClient, db_session, sample_retailer):
    headers = _admin_headers(client, db_session)
    mock_result = MagicMock()
    mock_result.id = "task-123"

    with patch("app.api.scrape.celery_app.send_task", return_value=mock_result) as send_task:
        response = client.post(f"/scrape/{sample_retailer.id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "enqueued"
    assert data["task_id"] == "task-123"
    send_task.assert_called_once()


def test_enqueue_scrape_requires_auth(client: TestClient, sample_retailer):
    response = client.post(f"/scrape/{sample_retailer.id}")
    assert response.status_code == 401


def test_enqueue_scrape_rejects_non_admin(client: TestClient, db_session, sample_retailer):
    headers = _user_headers(client, db_session)
    response = client.post(f"/scrape/{sample_retailer.id}", headers=headers)
    assert response.status_code == 403


def test_enqueue_scrape_not_found(client: TestClient, db_session):
    headers = _admin_headers(client, db_session)
    response = client.post("/scrape/404", headers=headers)
    assert response.status_code == 404


def test_enqueue_scrape_inactive_retailer(client: TestClient, db_session):
    headers = _admin_headers(client, db_session)
    retailer = Retailer(
        name="Inactive Shop",
        base_url="https://inactive.demo",
        scraping_config={},
        is_active=False,
    )
    db_session.add(retailer)
    db_session.commit()

    response = client.post(f"/scrape/{retailer.id}", headers=headers)
    assert response.status_code == 400


def test_enqueue_image_backfill_success(client: TestClient, db_session, sample_retailer):
    headers = _admin_headers(client, db_session)
    mock_result = MagicMock()
    mock_result.id = "backfill-1"

    with patch("app.api.scrape.celery_app.send_task", return_value=mock_result) as send_task:
        response = client.post("/scrape/images/backfill?limit=50", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "enqueued"
    assert data["task_id"] == "backfill-1"
    assert data["limit"] == 50
    assert "pending_estimate" in data
    send_task.assert_called_once()
    assert send_task.call_args.kwargs["kwargs"]["limit"] == 50


def test_enqueue_image_backfill_rejects_non_admin(client: TestClient, db_session):
    headers = _user_headers(client, db_session)
    response = client.post("/scrape/images/backfill", headers=headers)
    assert response.status_code == 403


def test_enqueue_image_backfill_unknown_retailer(client: TestClient, db_session):
    headers = _admin_headers(client, db_session)
    response = client.post("/scrape/images/backfill?retailer_id=9999", headers=headers)
    assert response.status_code == 404


def test_recommend_user_not_found(client: TestClient):
    response = client.get("/recommend/00000000-0000-0000-0000-000000000099")
    assert response.status_code == 404


def test_recommend_success(client: TestClient, sample_user, sample_product_with_price):
    response = client.get(f"/recommend/{sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(sample_user.id)
    assert len(data["recommendations"]) >= 1
