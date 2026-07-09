import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.models import Price, Product, Retailer, User


@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_retailer(db_session):
    retailer = Retailer(
        name="Test Boutique",
        base_url="https://test-boutique.demo",
        scraping_config={
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
            },
            "demo_items": [
                {
                    "external_id": "tb-01",
                    "name": "Linen Shirt",
                    "price": 89.0,
                    "brand": "Test Boutique",
                    "category": "casual",
                    "image_url": "https://example.com/shirt.jpg",
                }
            ],
        },
        is_active=True,
    )
    db_session.add(retailer)
    db_session.commit()
    db_session.refresh(retailer)
    return retailer


@pytest.fixture()
def sample_user(db_session):
    user = User(
        email="test@chicmatrix.app",
        name="Test User",
        height_cm=170.0,
        weight_kg=65.0,
        body_proportions={"waist_cm": 74},
        preferences={"colors": ["black"], "brands": ["Test Boutique"]},
        habits={"occasions": ["casual", "office"]},
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def sample_product_with_price(db_session, sample_retailer):
    product = Product(
        retailer_id=sample_retailer.id,
        external_id="tb-01",
        name="Linen Shirt",
        brand="Test Boutique",
        category="casual",
        color="black",
    )
    db_session.add(product)
    db_session.flush()
    db_session.add(
        Price(
            product_id=product.id,
            retailer_id=sample_retailer.id,
            amount=89.0,
            currency="USD",
        )
    )
    db_session.commit()
    db_session.refresh(product)
    return product
