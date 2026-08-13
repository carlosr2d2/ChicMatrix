from fastapi.testclient import TestClient

from app.models.enums import UserRole
from app.models.models import User
from app.services.password import hash_password


def _auth_headers(client: TestClient, db_session, email: str = "catalog@chicmatrix.app") -> dict:
    user = (
        db_session.query(User).filter(User.email == email).first()
    )
    if not user:
        user = User(
            email=email,
            password_hash=hash_password("SecurePass123"),
            name="Catalog User",
            verified=True,
            role=UserRole.USER.value,
            preferences={"colors": ["black"], "brands": ["Test Boutique"]},
            habits={"occasions": ["casual"]},
        )
        db_session.add(user)
        db_session.commit()

    login = client.post(
        "/login",
        json={"method": "email", "email": email, "password": "SecurePass123"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_list_products(client: TestClient, sample_product_with_price, sample_retailer):
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    item = data["items"][0]
    assert item["name"] == "Linen Shirt"
    assert item["retailer_name"] == sample_retailer.name
    assert item["latest_price"]["amount"] == 89.0
    assert item["image_url"] is None or isinstance(item["image_url"], str)
    assert "style_tags" in item
    assert "product_url" in item


def test_list_products_filter_by_retailer(client: TestClient, sample_product_with_price, sample_retailer):
    response = client.get(f"/products?retailer_id={sample_retailer.id}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1

    response_empty = client.get("/products?retailer_id=99999")
    assert response_empty.status_code == 200
    assert response_empty.json()["total"] == 0


def test_list_retailers(client: TestClient, sample_retailer):
    response = client.get("/retailers")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(r["name"] == sample_retailer.name for r in data["items"])


def test_get_my_profile(client: TestClient, db_session):
    headers = _auth_headers(client, db_session, email="me@chicmatrix.app")
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@chicmatrix.app"
    assert data["role"] == UserRole.USER.value
    assert "preferences" in data
    assert "habits" in data


def test_update_my_profile(client: TestClient, db_session):
    headers = _auth_headers(client, db_session, email="profile@chicmatrix.app")

    response = client.patch(
        "/users/me/profile",
        headers=headers,
        json={
            "height_cm": 175,
            "weight_kg": 70,
            "preferences": {"colors": ["navy", "beige"], "brands": ["Maison Noir"]},
            "habits": {"occasions": ["office", "casual"]},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["height_cm"] == 175
    assert data["preferences"]["colors"] == ["navy", "beige"]
    assert data["habits"]["occasions"] == ["office", "casual"]


def test_get_my_profile_requires_auth(client: TestClient):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_recommend_me(client: TestClient, db_session, sample_product_with_price):
    headers = _auth_headers(client, db_session, email="recommend@chicmatrix.app")

    # ensure preferences match sample product brand/category
    client.patch(
        "/users/me/profile",
        headers=headers,
        json={
            "preferences": {"colors": ["black"], "brands": ["Test Boutique"]},
            "habits": {"occasions": ["casual"]},
        },
    )

    response = client.get("/recommend/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) >= 1
    item = data["recommendations"][0]
    assert item["product"]["name"] == "Linen Shirt"
    assert isinstance(item["score"], (int, float))
    assert isinstance(item["reasons"], list)
    assert isinstance(item["prices"], list)
    assert "best_price" in item


def test_recommend_me_requires_auth(client: TestClient):
    response = client.get("/recommend/me")
    assert response.status_code == 401
