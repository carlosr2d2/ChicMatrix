import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.enums import UserRole
from app.models.models import Retailer, StyleTag, User
from app.services.password import hash_password
from app.services.style_tagging import ensure_style_tags

logger = logging.getLogger(__name__)

COMMON_SELECTORS = {
    "item": "article.product",
    "name": ".product-title",
    "price": ".price",
    "image": "img",
    "link": "a",
    "brand": ".brand",
    "category": ".category",
    "color": ".color",
    "description": ".description",
}

# Public practice storefront (SSR HTML). Snapshot also kept for offline CI:
# fixtures/scraping/automation_exercise_products.html
LIVE_HTTP_SELECTORS = {
    "item": ".product-image-wrapper",
    "name": ".productinfo p",
    "price": ".productinfo h2",
    "image": ".productinfo img",
    "link": "a[href*='product_details']",
    "default_category": "casual",
}

DEMO_RETAILERS = [
    {
        "name": "Maison Noir",
        "base_url": "https://maison-noir.demo",
        "scraping_config": {
            "engine": "httpx",
            "listing_url": "fixture://maison_noir.html",
            "currency": "USD",
            "selectors": {
                **COMMON_SELECTORS,
                "default_category": "evening",
            },
        },
    },
    {
        "name": "Urban Loom",
        "base_url": "https://urban-loom.demo",
        "scraping_config": {
            "engine": "httpx",
            "listing_url": "fixture://urban_loom.html",
            "currency": "USD",
            "selectors": {
                **COMMON_SELECTORS,
                "default_category": "casual",
            },
        },
    },
    {
        "name": "Atelier Vue",
        "base_url": "https://atelier-vue.demo",
        "scraping_config": {
            # Demo uses the same fixture path as httpx; switch listing_url to a live
            # JS storefront and keep engine=playwright for real browser scraping.
            "engine": "httpx",
            "listing_url": "fixture://atelier_vue.html",
            "wait_selector": ".product-card",
            "wait_until": "networkidle",
            "currency": "USD",
            "selectors": {
                **COMMON_SELECTORS,
                "default_category": "evening",
            },
        },
    },
    {
        "name": "Practice Boutique",
        "base_url": "https://automationexercise.com",
        "scraping_config": {
            "engine": "httpx",
            # Live HTTP listing (admin-triggered, single page). Offline tests use
            # fixture://automation_exercise_products.html with the same selectors.
            "listing_url": "https://automationexercise.com/products",
            "request_delay_ms": 500,
            "enrich_product_details": True,
            "detail_selectors": {
                "root": ".product-information",
            },
            "headers": {
                "User-Agent": (
                    "ChicMatrixBot/1.0 (+https://github.com/carlosr2d2/ChicMatrix; demo)"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
            "currency": "INR",
            "selectors": LIVE_HTTP_SELECTORS,
        },
    },
]

DEMO_USER = {
    "email": "demo@chicmatrix.app",
    "name": "Alex Rivera",
    "password_hash": hash_password("DemoPass123"),
    "verified": True,
    "consent_given_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "consent_version": "1.0",
    "height_cm": 172.0,
    "weight_kg": 68.0,
    "body_proportions": {"waist_cm": 76, "hips_cm": 98, "shoulders_cm": 42},
    "preferences": {
        "colors": ["black", "beige", "grey"],
        "brands": ["Maison Noir", "Urban Loom"],
        "styles": ["formal", "minimal", "casual"],
    },
    "habits": {"occasions": ["office", "evening", "casual"], "lifestyle": "urban professional"},
}

ADMIN_USER = {
    "email": "admin@chicmatrix.app",
    "name": "System Admin",
    "password_hash": hash_password("AdminPass123"),
    "verified": True,
    "role": UserRole.ADMIN.value,
    "consent_given_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    "consent_version": "1.0",
}


def seed_database(db: Session) -> None:
    ensure_style_tags(db)

    for data in DEMO_RETAILERS:
        exists = db.query(Retailer).filter(Retailer.name == data["name"]).first()
        if not exists:
            db.add(Retailer(**data, is_active=True))
        else:
            # Keep scrape configs current across deploys (fixtures replace demo_items).
            exists.base_url = data["base_url"]
            exists.scraping_config = data["scraping_config"]
            exists.is_active = True

    user = db.query(User).filter(User.email == DEMO_USER["email"]).first()
    if not user:
        db.add(User(**DEMO_USER))
    else:
        if not user.password_hash:
            user.password_hash = DEMO_USER["password_hash"]
            user.verified = True
        # Keep demo style preferences aligned with taxonomy v1.
        prefs = dict(user.preferences or {})
        prefs.setdefault("styles", DEMO_USER["preferences"]["styles"])
        user.preferences = prefs

    admin = db.query(User).filter(User.email == ADMIN_USER["email"]).first()
    if not admin:
        db.add(User(**ADMIN_USER))
    elif admin.role != UserRole.ADMIN.value:
        admin.role = UserRole.ADMIN.value
        if not admin.password_hash:
            admin.password_hash = ADMIN_USER["password_hash"]
        admin.verified = True

    db.commit()
    logger.info(
        "Seed data applied",
        extra={"style_tags": db.query(StyleTag).count()},
    )


def run_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_seed()
