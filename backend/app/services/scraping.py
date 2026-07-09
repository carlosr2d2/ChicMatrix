import logging
import re
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.models import Price, Product, Retailer
from app.services.browser_fetcher import PlaywrightFetcher

logger = logging.getLogger(__name__)


class ScrapingService:
  """Configurable scraper driven by retailer.scraping_config rules."""

  def __init__(self, db: Session):
    self.db = db

  def scrape_retailer(self, retailer_id: int) -> dict:
    retailer = self.db.query(Retailer).filter(Retailer.id == retailer_id).first()
    if not retailer:
      raise ValueError(f"Retailer {retailer_id} not found")

    config = retailer.scraping_config or {}
    selectors = config.get("selectors", {})

    if config.get("demo_items"):
      items = self._demo_items(config["demo_items"])
    else:
      listing_url = config.get("listing_url", retailer.base_url)
      headers = config.get("headers", {"User-Agent": "ChicMatrixBot/1.0"})
      logger.info("Starting scrape", extra={"retailer": retailer.name, "url": listing_url})

      html = self._fetch_html(listing_url, config, headers)
      soup = BeautifulSoup(html, "lxml")
      item_selector = selectors.get("item", "article.product, .product-card, li.product")
      items = soup.select(item_selector)

    created = 0
    updated = 0

    for idx, item in enumerate(items):
      product_data = self._parse_item(item, selectors, retailer, idx)
      if not product_data:
        continue

      price_amount = product_data.pop("price", None)

      existing = (
        self.db.query(Product)
        .filter(
          Product.retailer_id == retailer.id,
          Product.external_id == product_data["external_id"],
        )
        .first()
      )

      if existing:
        for key, value in product_data.items():
          if key != "external_id" and value is not None:
            setattr(existing, key, value)
        product = existing
        updated += 1
      else:
        product = Product(retailer_id=retailer.id, **product_data)
        self.db.add(product)
        self.db.flush()
        created += 1

      if price_amount is not None:
        self.db.add(
          Price(
            product_id=product.id,
            retailer_id=retailer.id,
            amount=price_amount,
            currency=config.get("currency", "USD"),
            scraped_at=datetime.now(timezone.utc),
          )
        )

    self.db.commit()
    result = {
      "retailer_id": retailer_id,
      "products_created": created,
      "products_updated": updated,
      "total": created + updated,
    }
    logger.info("Scrape completed", extra=result)
    return result

  def _fetch_html(self, url: str, config: dict, headers: dict) -> str:
    engine = config.get("engine", "httpx")
    if engine == "playwright":
      if not PlaywrightFetcher.is_available():
        raise RuntimeError("Playwright is not installed; use engine 'httpx' or install playwright")
      playwright_config = {**config, "headers": headers}
      return PlaywrightFetcher().fetch_html(url, playwright_config)

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
      response = client.get(url, headers=headers)
      response.raise_for_status()
      return response.text

  def _parse_item(self, item, selectors: dict, retailer: Retailer, idx: int) -> dict | None:
    name_sel = selectors.get("name", "h2, h3, .product-title, .title")
    price_sel = selectors.get("price", ".price, .product-price, [data-price]")
    image_sel = selectors.get("image", "img")
    link_sel = selectors.get("link", "a")
    brand_sel = selectors.get("brand", ".brand")
    category_sel = selectors.get("category", ".category")

    name_el = item.select_one(name_sel)
    name = name_el.get_text(strip=True) if name_el else None
    if not name:
      return None

    price_el = item.select_one(price_sel)
    price = self._parse_price(price_el.get_text() if price_el else None)
    if price_el and price_el.get("data-price"):
      price = self._parse_price(price_el["data-price"])

    image_el = item.select_one(image_sel)
    image_url = None
    if image_el:
      image_url = image_el.get("src") or image_el.get("data-src")
      if image_url and image_url.startswith("/"):
        image_url = retailer.base_url.rstrip("/") + image_url

    link_el = item.select_one(link_sel)
    external_id = None
    if link_el and link_el.get("href"):
      href = link_el["href"]
      external_id = href.rstrip("/").split("/")[-1]
    else:
      external_id = f"{retailer.name.lower()}-{idx}"

    brand_el = item.select_one(brand_sel)
    category_el = item.select_one(category_sel)

    return {
      "external_id": external_id,
      "name": name,
      "description": None,
      "image_url": image_url,
      "brand": brand_el.get_text(strip=True) if brand_el else None,
      "category": category_el.get_text(strip=True) if category_el else selectors.get("default_category"),
      "color": selectors.get("default_color"),
      "price": price,
    }

  def _demo_items(self, demo_items: list[dict]) -> list:
    """Build synthetic DOM nodes from seed data for offline/demo retailers."""
    html_parts = []
    for item in demo_items:
      html_parts.append(
        f'<article class="product">'
        f'<h3 class="product-title">{item["name"]}</h3>'
        f'<span class="price">{item.get("price", 0)}</span>'
        f'<img src="{item.get("image_url", "")}" />'
        f'<a href="/product/{item.get("external_id", item["name"])}"></a>'
        f'<span class="brand">{item.get("brand", "")}</span>'
        f'<span class="category">{item.get("category", "")}</span>'
        f"</article>"
      )
    soup = BeautifulSoup("".join(html_parts), "lxml")
    return soup.select("article.product")

  @staticmethod
  def _parse_price(raw: str | None) -> float | None:
    if not raw:
      return None
    match = re.search(r"[\d,.]+", raw.replace(",", ""))
    if not match:
      return None
    try:
      return float(match.group())
    except ValueError:
      return None
