import logging

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.models import Retailer, User

logger = logging.getLogger(__name__)

DEMO_RETAILERS = [
    {
        "name": "Maison Noir",
        "base_url": "https://maison-noir.demo",
        "scraping_config": {
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
                "default_category": "evening",
            },
            "demo_items": [
                {
                    "external_id": "mn-blazer-01",
                    "name": "Structured Wool Blazer",
                    "price": 289.0,
                    "brand": "Maison Noir",
                    "category": "evening",
                    "image_url": "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=600",
                },
                {
                    "external_id": "mn-trouser-01",
                    "name": "Tailored Wide Leg Trouser",
                    "price": 165.0,
                    "brand": "Maison Noir",
                    "category": "office",
                    "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=600",
                },
                {
                    "external_id": "mn-dress-01",
                    "name": "Silk Midi Dress",
                    "price": 420.0,
                    "brand": "Maison Noir",
                    "category": "evening",
                    "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600",
                },
            ],
        },
    },
    {
        "name": "Urban Loom",
        "base_url": "https://urban-loom.demo",
        "scraping_config": {
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
                "default_category": "casual",
            },
            "demo_items": [
                {
                    "external_id": "ul-knit-01",
                    "name": "Cashmere Crewneck",
                    "price": 198.0,
                    "brand": "Urban Loom",
                    "category": "casual",
                    "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600",
                },
                {
                    "external_id": "ul-coat-01",
                    "name": "Minimalist Wool Coat",
                    "price": 345.0,
                    "brand": "Urban Loom",
                    "category": "outerwear",
                    "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=600",
                },
                {
                    "external_id": "ul-denim-01",
                    "name": "Selvedge Straight Denim",
                    "price": 128.0,
                    "brand": "Urban Loom",
                    "category": "casual",
                    "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600",
                },
            ],
        },
    },
    {
        "name": "Atelier Vue",
        "base_url": "https://atelier-vue.demo",
        "scraping_config": {
            "engine": "playwright",
            "listing_url": "https://atelier-vue.demo/new-arrivals",
            "wait_selector": ".product-card",
            "wait_until": "networkidle",
            "currency": "USD",
            "selectors": {
                "item": "article.product",
                "name": ".product-title",
                "price": ".price",
                "image": "img",
                "link": "a",
                "brand": ".brand",
                "category": ".category",
                "default_category": "evening",
            },
            "demo_items": [
                {
                    "external_id": "av-gown-01",
                    "name": "Draped Evening Gown",
                    "price": 510.0,
                    "brand": "Atelier Vue",
                    "category": "evening",
                    "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600",
                }
            ],
        },
    },
]

DEMO_USER = {
    "email": "demo@chicmatrix.app",
    "name": "Alex Rivera",
    "height_cm": 172.0,
    "weight_kg": 68.0,
    "body_proportions": {"waist_cm": 76, "hips_cm": 98, "shoulders_cm": 42},
    "preferences": {"colors": ["black", "beige", "grey"], "brands": ["Maison Noir", "Urban Loom"]},
    "habits": {"occasions": ["office", "evening", "casual"], "lifestyle": "urban professional"},
}


def seed_database(db: Session) -> None:
    for data in DEMO_RETAILERS:
        exists = db.query(Retailer).filter(Retailer.name == data["name"]).first()
        if not exists:
            db.add(Retailer(**data, is_active=True))

    user = db.query(User).filter(User.email == DEMO_USER["email"]).first()
    if not user:
        db.add(User(**DEMO_USER))

    db.commit()
    logger.info("Seed data applied")


def run_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_seed()
