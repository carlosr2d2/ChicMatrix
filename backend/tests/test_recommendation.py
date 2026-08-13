from app.models.models import Product
from app.services.recommendation import RecommendationEngine
from app.services.style_tagging import apply_style_classification, ensure_style_tags


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


def test_recommend_boosts_matching_style_tags(db_session, sample_user, sample_retailer):
    ensure_style_tags(db_session)
    sample_user.preferences = {
        **(sample_user.preferences or {}),
        "styles": ["formal"],
        "brands": [],
        "colors": [],
    }
    sample_user.habits = {"occasions": []}
    db_session.commit()

    formal = Product(
        retailer_id=sample_retailer.id,
        external_id="formal-1",
        name="Tailored Formal Blazer",
        description="Tailored formal office blazer with clean lines",
        brand="Other",
        category="evening",
    )
    other = Product(
        retailer_id=sample_retailer.id,
        external_id="sport-1",
        name="Gym Tank",
        description="Athletic gym training tank",
        brand="Other",
        category="sport",
    )
    db_session.add_all([formal, other])
    db_session.flush()
    apply_style_classification(db_session, formal)
    apply_style_classification(db_session, other)
    db_session.commit()

    engine = RecommendationEngine(db_session)
    recommendations = engine.recommend(sample_user, limit=2)

    assert recommendations[0].product.name == "Tailored Formal Blazer"
    assert any("Matches style" in reason for reason in recommendations[0].reasons)
    assert any(tag.code == "formal" for tag in recommendations[0].product.style_tags)


def test_recommend_excludes_opposite_sex_products(db_session, sample_user, sample_retailer):
    sample_user.sex = "male"
    sample_user.preferences = {
        "colors": ["black"],
        "brands": ["Shared Brand"],
        "styles": ["casual"],
    }
    sample_user.habits = {"occasions": ["casual"]}
    db_session.commit()

    womens = Product(
        retailer_id=sample_retailer.id,
        external_id="w-1",
        name="Blue Top",
        description="Category: Women > Tops",
        brand="Shared Brand",
        category="casual",
        color="black",
    )
    dress = Product(
        retailer_id=sample_retailer.id,
        external_id="w-2",
        name="Silk Midi Dress",
        description="Elegant evening dress",
        brand="Shared Brand",
        category="casual",
        color="black",
    )
    mens = Product(
        retailer_id=sample_retailer.id,
        external_id="m-1",
        name="Men Tshirt",
        description="Category: Men > Tshirts",
        brand="Shared Brand",
        category="casual",
        color="black",
    )
    unisex = Product(
        retailer_id=sample_retailer.id,
        external_id="u-1",
        name="Cashmere Crewneck",
        description="Everyday casual crewneck",
        brand="Shared Brand",
        category="casual",
        color="black",
    )
    db_session.add_all([womens, dress, mens, unisex])
    db_session.commit()

    engine = RecommendationEngine(db_session)
    recommendations = engine.recommend(sample_user, limit=10)
    names = {item.product.name for item in recommendations}

    assert "Blue Top" not in names
    assert "Silk Midi Dress" not in names
    assert "Men Tshirt" in names
    assert "Cashmere Crewneck" in names
