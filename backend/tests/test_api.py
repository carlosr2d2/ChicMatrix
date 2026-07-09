from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.models.models import Retailer


def test_enqueue_scrape_success(client: TestClient, db_session, sample_retailer):
    mock_result = MagicMock()
    mock_result.id = "task-123"

    with patch("app.api.scrape.celery_app.send_task", return_value=mock_result) as send_task:
        response = client.post(f"/scrape/{sample_retailer.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "enqueued"
    assert data["task_id"] == "task-123"
    send_task.assert_called_once()


def test_enqueue_scrape_not_found(client: TestClient):
    response = client.post("/scrape/404")
    assert response.status_code == 404


def test_enqueue_scrape_inactive_retailer(client: TestClient, db_session):
    retailer = Retailer(
        name="Inactive Shop",
        base_url="https://inactive.demo",
        scraping_config={},
        is_active=False,
    )
    db_session.add(retailer)
    db_session.commit()

    response = client.post(f"/scrape/{retailer.id}")
    assert response.status_code == 400


def test_recommend_user_not_found(client: TestClient):
    response = client.get("/recommend/999")
    assert response.status_code == 404


def test_recommend_success(client: TestClient, sample_user, sample_product_with_price):
    response = client.get(f"/recommend/{sample_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == sample_user.id
    assert len(data["recommendations"]) >= 1
