import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.models import Price, Product, Retailer
from app.services.browser_fetcher import PlaywrightFetcher
from app.services.image_cache import cache_product_image
from app.services.style_tagging import apply_style_classification

logger = logging.getLogger(__name__)
DEFAULT_BOT_UA = "ChicMatrixBot/1.0 (+https://github.com/carlosr2d2/ChicMatrix; demo)"
COLOR_WORDS = (
  "black",
  "white",
  "blue",
  "pink",
  "green",
  "grey",
  "gray",
  "red",
  "beige",
  "brown",
  "yellow",
  "purple",
  "orange",
  "navy",
)


def scraping_fixtures_dir() -> Path:
  env = os.getenv("SCRAPING_FIXTURES_DIR")
  if env:
    return Path(env)
  # backend/app/services/scraping.py -> backend/fixtures/scraping
  return Path(__file__).resolve().parents[2] / "fixtures" / "scraping"


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
    headers = config.get("headers") or {"User-Agent": DEFAULT_BOT_UA}
    if "User-Agent" not in headers:
      headers = {**headers, "User-Agent": DEFAULT_BOT_UA}

    if config.get("demo_items"):
      items = self._demo_items(config["demo_items"])
    else:
      listing_url = config.get("listing_url", retailer.base_url)
      logger.info("Starting scrape", extra={"retailer": retailer.name, "url": listing_url})

      html = self._fetch_html(listing_url, config, headers)
      soup = BeautifulSoup(html, "lxml")
      item_selector = selectors.get("item", "article.product, .product-card, li.product")
      items = soup.select(item_selector)

    created = 0
    updated = 0
    classified = 0
    details_enriched = 0
    images_cached = 0

    for idx, item in enumerate(items):
      product_data = self._parse_item(item, selectors, retailer, idx)
      if not product_data:
        continue

      if config.get("enrich_product_details") and self._enrich_product_details(
        product_data, config, headers
      ):
        details_enriched += 1

      self._apply_field_fallbacks(product_data, retailer, selectors)

      price_amount = product_data.pop("price", None)
      # Preserve remote URL for disk cache; do not overwrite an already-cached local path
      # until we know the download succeeded.
      remote_image = product_data.get("image_url")

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
          if key == "external_id" or value is None:
            continue
          if key == "image_url" and existing.image_url and "/media/products/" in existing.image_url:
            # Keep local path until cache_product_image refreshes it.
            continue
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

      apply_style_classification(self.db, product)
      classified += 1

      if config.get("cache_images", True):
        cached = cache_product_image(
          product,
          source_url=remote_image or product.image_source_url,
          headers=headers,
        )
        if cached:
          images_cached += 1

    self.db.commit()
    result = {
      "retailer_id": retailer_id,
      "products_created": created,
      "products_updated": updated,
      "products_classified": classified,
      "details_enriched": details_enriched,
      "images_cached": images_cached,
      "total": created + updated,
    }
    logger.info("Scrape completed", extra=result)
    return result

  def _fetch_html(self, url: str, config: dict, headers: dict) -> str:
    local_html = self._read_local_listing(url, config)
    if local_html is not None:
      return local_html

    self._polite_delay(config)
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

  @staticmethod
  def _polite_delay(config: dict) -> None:
    """Optional pause before live HTTP/Playwright fetches (skipped for fixtures)."""
    delay_ms = config.get("request_delay_ms", 0)
    try:
      delay_ms = int(delay_ms)
    except (TypeError, ValueError):
      delay_ms = 0
    if delay_ms > 0:
      time.sleep(delay_ms / 1000.0)

  def _read_local_listing(self, url: str, config: dict) -> str | None:
    """Load HTML from fixture:// or file:// so scrapes stay demo-safe offline."""
    fixture_name = config.get("fixture")
    parsed = urlparse(url)

    if fixture_name:
      path = scraping_fixtures_dir() / fixture_name
    elif parsed.scheme == "fixture":
      name = unquote(parsed.netloc or parsed.path).lstrip("/")
      if not name:
        raise ValueError(f"Invalid fixture listing_url: {url}")
      path = scraping_fixtures_dir() / name
    elif parsed.scheme == "file":
      raw_path = unquote(parsed.path)
      if os.name == "nt" and re.match(r"^/[A-Za-z]:", raw_path):
        raw_path = raw_path[1:]
      path = Path(raw_path)
    else:
      return None

    if not path.is_file():
      raise FileNotFoundError(f"Scraping fixture not found: {path}")

    logger.info("Loading scrape fixture", extra={"path": str(path)})
    return path.read_text(encoding="utf-8")

  def _parse_item(self, item, selectors: dict, retailer: Retailer, idx: int) -> dict | None:
    name_sel = selectors.get("name", "h2, h3, .product-title, .title")
    price_sel = selectors.get("price", ".price, .product-price, [data-price]")
    image_sel = selectors.get("image", "img")
    link_sel = selectors.get("link", "a")
    brand_sel = selectors.get("brand", ".brand")
    category_sel = selectors.get("category", ".category")
    color_sel = selectors.get("color", ".color, [data-color]")
    description_sel = selectors.get("description", ".description, .product-description, p.desc")

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
    product_url = None
    if link_el and link_el.get("href"):
      href = link_el["href"]
      product_url = urljoin(retailer.base_url.rstrip("/") + "/", href)
      external_id = href.rstrip("/").split("/")[-1] or None
    if not external_id:
      external_id = f"{retailer.name.lower().replace(' ', '-')}-{idx}"

    brand_el = item.select_one(brand_sel)
    category_el = item.select_one(category_sel)
    color_el = item.select_one(color_sel)
    description_el = item.select_one(description_sel)

    color = None
    if color_el:
      color = color_el.get("data-color") or color_el.get_text(strip=True)
    if not color:
      color = selectors.get("default_color")

    description = None
    if description_el:
      description = description_el.get_text(" ", strip=True) or None

    brand = brand_el.get_text(strip=True) if brand_el else None

    return {
      "external_id": external_id,
      "name": name,
      "description": description,
      "image_url": image_url,
      "product_url": product_url,
      "brand": brand,
      "category": category_el.get_text(strip=True) if category_el else selectors.get("default_category"),
      "color": color,
      "price": price,
    }

  def _enrich_product_details(self, product_data: dict, config: dict, headers: dict) -> bool:
    """Fetch product PDP to fill brand/category/description when listing cards are thin."""
    product_url = product_data.get("product_url")
    if not product_url or not str(product_url).startswith(("http://", "https://")):
      return False

    try:
      html = self._fetch_html(product_url, config, headers)
    except Exception as exc:  # noqa: BLE001 - keep listing scrape resilient
      logger.warning(
        "Detail enrich failed",
        extra={"url": product_url, "error": str(exc)},
      )
      return False

    detail = self.extract_detail_fields(html, config.get("detail_selectors") or {})
    changed = False
    if detail.get("brand") and not product_data.get("brand"):
      product_data["brand"] = detail["brand"]
      changed = True
    if detail.get("category_label"):
      # Keep listing default_category for style rules; put PDP taxonomy in description.
      label = detail["category_label"]
      existing = product_data.get("description") or product_data.get("name") or ""
      snippet = f"Category: {label}"
      if snippet.lower() not in existing.lower():
        product_data["description"] = f"{existing}. {snippet}".strip(". ").replace("..", ".")
        changed = True
    if detail.get("description"):
      existing = product_data.get("description") or ""
      if detail["description"] not in existing:
        product_data["description"] = (
          f"{existing}. {detail['description']}".strip(". ") if existing else detail["description"]
        )
        changed = True
    return changed

  def _apply_field_fallbacks(self, product_data: dict, retailer: Retailer, selectors: dict) -> None:
    if not product_data.get("brand"):
      product_data["brand"] = retailer.name
    if not product_data.get("color"):
      product_data["color"] = self.infer_color_from_text(product_data.get("name") or "")
    if not product_data.get("color"):
      product_data["color"] = selectors.get("default_color")
    if not product_data.get("description"):
      bits = [product_data.get("name") or ""]
      if product_data.get("category"):
        bits.append(f"Category: {product_data['category']}")
      if product_data.get("color"):
        bits.append(f"Color: {product_data['color']}")
      product_data["description"] = ". ".join(b for b in bits if b)

  @staticmethod
  def extract_detail_fields(html: str, detail_selectors: dict) -> dict:
    soup = BeautifulSoup(html, "lxml")
    root_sel = detail_selectors.get("root", ".product-information")
    root = soup.select_one(root_sel) or soup

    brand = None
    category_label = None
    description = None

    brand_sel = detail_selectors.get("brand")
    if brand_sel:
      el = root.select_one(brand_sel)
      if el:
        brand = el.get_text(" ", strip=True) or None

    category_sel = detail_selectors.get("category")
    if category_sel:
      el = root.select_one(category_sel)
      if el:
        raw = el.get_text(" ", strip=True)
        category_label = raw.split(":", 1)[-1].strip() if raw else None

    description_sel = detail_selectors.get("description")
    if description_sel:
      el = root.select_one(description_sel)
      if el:
        description = el.get_text(" ", strip=True) or None

    # Heuristic parse for practice sites that use <p><b>Brand:</b> Polo</p>
    if not brand or not category_label:
      for p in root.select("p"):
        text = p.get_text(" ", strip=True)
        lower = text.lower()
        if not category_label and lower.startswith("category:"):
          category_label = text.split(":", 1)[-1].strip()
        if not brand and lower.startswith("brand:"):
          brand = text.split(":", 1)[-1].strip()

    return {
      "brand": brand or None,
      "category_label": category_label or None,
      "description": description or None,
    }

  @staticmethod
  def infer_color_from_text(text: str) -> str | None:
    tokens = set(re.findall(r"[a-z]+", (text or "").lower()))
    for color in COLOR_WORDS:
      if color in tokens:
        return color
    return None

  def _demo_items(self, demo_items: list[dict]) -> list:
    """Build synthetic DOM nodes from seed data for offline/demo retailers."""
    html_parts = []
    for item in demo_items:
      color = item.get("color", "")
      description = item.get("description", "")
      html_parts.append(
        f'<article class="product">'
        f'<h3 class="product-title">{item["name"]}</h3>'
        f'<span class="price">{item.get("price", 0)}</span>'
        f'<img src="{item.get("image_url", "")}" />'
        f'<a href="/product/{item.get("external_id", item["name"])}"></a>'
        f'<span class="brand">{item.get("brand", "")}</span>'
        f'<span class="category">{item.get("category", "")}</span>'
        f'<span class="color">{color}</span>'
        f'<p class="description">{description}</p>'
        f"</article>"
      )
    soup = BeautifulSoup("".join(html_parts), "lxml")
    return soup.select("article.product")

  @staticmethod
  def _parse_price(raw: str | None) -> float | None:
    if not raw:
      return None
    # Require a digit so currency dots like "Rs." are not treated as amounts.
    cleaned = raw.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    if not match:
      return None
    try:
      return float(match.group())
    except ValueError:
      return None
