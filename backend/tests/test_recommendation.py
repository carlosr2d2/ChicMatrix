from app.models.models import Product
from app.services.recommendation import RecommendationEngine


def test_recommend_returns_matching_brand(db_session, sample_user, sample_product_with_price):
    engine = RecommendationEngine(db_session)
    recommendations = engine.recommend(sample_user, limit=5)

    assert len(recommendations) == 1
    item = recommendations[0]
    assert item.product.name == "Linen Shirt"
    assert item.score > 0
    assert any("Test Boutique" in reason for reason in item.reasons)
    assert item.best_price is not None
    assert item.best_price.amount == 89.0


def test_recommend_empty_catalog(db_session, sample_user):
    engine = RecommendationEngine(db_session)
    recommendations = engine.recommend(sample_user, limit=5)
    assert recommendations == []


def test_recommend_prefers_higher_scores(db_session, sample_user, sample_retailer):
    products = [
        Product(
            retailer_id=sample_retailer.id,
            external_id="low",
            name="Basic Tee",
            brand="Other Brand",
            category="sport",
        ),
        Product(
            retailer_id=sample_retailer.id,
            external_id="high",
            name="Linen Shirt",
            brand="Test Boutique",
            category="casual",
            color="black",
        ),
    ]
    db_session.add_all(products)
    db_session.commit()

    engine = RecommendationEngine(db_session)
    recommendations = engine.recommend(sample_user, limit=2)

    assert recommendations[0].product.name == "Linen Shirt"
    assert recommendations[0].score >= recommendations[1].score
