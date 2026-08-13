from pathlib import Path

import pytest

from app.models.models import Price, Product, Retailer
from app.services.scraping import ScrapingService, scraping_fixtures_dir


def test_scrape_demo_retailer_creates_products(db_session, sample_retailer):
    service = ScrapingService(db_session)
    result = service.scrape_retailer(sample_retailer.id)

    assert result["products_created"] == 1
    assert result["total"] == 1

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


def test_scrape_fixture_listing_creates_products_and_prices(db_session):
    fixture = scraping_fixtures_dir() / "maison_noir.html"
    assert fixture.is_file()

    retailer = Retailer(
        name="Fixture Boutique",
        base_url="https://fixture-boutique.demo",
        scraping_config={
            "engine": "httpx",
            "listing_url": "fixture://maison_noir.html",
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
                "color": ".color",
                "description": ".description",
            },
        },
        is_active=True,
    )
    db_session.add(retailer)
    db_session.commit()
    db_session.refresh(retailer)

    service = ScrapingService(db_session)
    result = service.scrape_retailer(retailer.id)

    assert result["products_created"] == 5
    assert result["total"] == 5
    assert result["products_classified"] == 5

    products = (
        db_session.query(Product).filter(Product.retailer_id == retailer.id).order_by(Product.id).all()
    )
    prices = db_session.query(Price).filter(Price.retailer_id == retailer.id).all()

    assert {p.name for p in products} >= {
        "Structured Wool Blazer",
        "Cashmere Crewneck",
        "Leather Biker Jacket",
    }
    blazer = next(p for p in products if p.name == "Structured Wool Blazer")
    assert blazer.brand == "Maison Noir"
    assert blazer.color == "black"
    assert blazer.description and "formal" in blazer.description.lower()
    assert blazer.product_url and blazer.product_url.endswith("/product/mn-blazer-01")
    assert blazer.image_url and blazer.image_url.startswith("https://")
    assert len(prices) == 5
    assert any(price.amount == 289.0 for price in prices)

    from app.models.models import ProductStyleTag

    assignments = (
        db_session.query(ProductStyleTag).filter(ProductStyleTag.product_id == blazer.id).all()
    )
    assert len(assignments) >= 1
    assert any(a.score >= 0.45 for a in assignments)


def test_scrape_file_listing_url(db_session, tmp_path):
    html = """
    <article class="product">
      <h3 class="product-title">Local Coat</h3>
      <span class="price" data-price="99">$99</span>
      <img src="https://example.com/coat.jpg" />
      <a href="/product/local-coat"></a>
      <span class="brand">Local Brand</span>
      <span class="category">outerwear</span>
      <span class="color">grey</span>
    </article>
    """
    fixture_path = tmp_path / "local.html"
    fixture_path.write_text(html, encoding="utf-8")
    listing_url = fixture_path.resolve().as_uri()

    retailer = Retailer(
        name="File Boutique",
        base_url="https://file-boutique.demo",
        scraping_config={
            "engine": "httpx",
            "listing_url": listing_url,
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
                "color": ".color",
            },
        },
        is_active=True,
    )
    db_session.add(retailer)
    db_session.commit()
    db_session.refresh(retailer)

    result = ScrapingService(db_session).scrape_retailer(retailer.id)
    assert result["products_created"] == 1
    product = db_session.query(Product).filter(Product.retailer_id == retailer.id).one()
    assert product.name == "Local Coat"
    assert product.color == "grey"


def test_missing_fixture_raises(db_session):
    retailer = Retailer(
        name="Missing Fixture Shop",
        base_url="https://missing.demo",
        scraping_config={
            "engine": "httpx",
            "listing_url": "fixture://does_not_exist.html",
            "currency": "USD",
            "selectors": {"item": "article.product", "name": ".product-title"},
        },
        is_active=True,
    )
    db_session.add(retailer)
    db_session.commit()
    db_session.refresh(retailer)

    with pytest.raises(FileNotFoundError, match="does_not_exist"):
        ScrapingService(db_session).scrape_retailer(retailer.id)


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


def test_scraping_fixtures_dir_contains_seed_html():
    fixtures = scraping_fixtures_dir()
    assert (fixtures / "maison_noir.html").is_file()
    assert (fixtures / "urban_loom.html").is_file()
    assert (fixtures / "atelier_vue.html").is_file()
    assert Path(fixtures).name == "scraping"
