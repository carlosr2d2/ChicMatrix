import pytest

from app.services.scraping import ScrapingService


def test_scrape_demo_retailer_creates_products(db_session, sample_retailer):
    service = ScrapingService(db_session)
    result = service.scrape_retailer(sample_retailer.id)

    assert result["products_created"] == 1
    assert result["total"] == 1

    from app.models.models import Product, Price

    products = db_session.query(Product).all()
    prices = db_session.query(Price).all()
    assert len(products) == 1
    assert products[0].name == "Linen Shirt"
    assert len(prices) == 1
    assert prices[0].amount == 89.0


def test_scrape_updates_existing_product(db_session, sample_retailer):
    service = ScrapingService(db_session)
    service.scrape_retailer(sample_retailer.id)
    result = service.scrape_retailer(sample_retailer.id)

    assert result["products_created"] == 0
    assert result["products_updated"] == 1


def test_scrape_unknown_retailer_raises(db_session):
    service = ScrapingService(db_session)
    with pytest.raises(ValueError, match="not found"):
        service.scrape_retailer(999)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("$129.99", 129.99),
        ("1,299.00", 1299.0),
        ("invalid", None),
        (None, None),
    ],
)
def test_parse_price(raw, expected):
    assert ScrapingService._parse_price(raw) == expected
