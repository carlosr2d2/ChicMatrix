from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.models import Product, ProductStyleTag, StyleTag
from app.services.style_classifier_factory import get_style_classifier


def ensure_style_tags(db: Session) -> dict[str, StyleTag]:
    """Idempotently seed closed vocabulary rows; return code -> StyleTag map."""
    from app.models.enums import STYLE_TAG_CATALOG

    existing = {t.code: t for t in db.query(StyleTag).all()}
    created = False
    for row in STYLE_TAG_CATALOG:
        if row["code"] not in existing:
            tag = StyleTag(code=row["code"], label_es=row["label_es"], active=True)
            db.add(tag)
            created = True
    if created:
        db.flush()
        existing = {t.code: t for t in db.query(StyleTag).all()}
    return existing


def apply_style_classification(db: Session, product: Product) -> list[ProductStyleTag]:
    """Replace style assignments for a product using the configured classifier."""
    tags_by_code = ensure_style_tags(db)
    result = get_style_classifier().classify(
        name=product.name,
        description=product.description,
        brand=product.brand,
        category=product.category,
        color=product.color,
    )

    db.query(ProductStyleTag).filter(ProductStyleTag.product_id == product.id).delete()
    assignments: list[ProductStyleTag] = []
    now = datetime.now(timezone.utc)
    for scored in result.tags:
        tag = tags_by_code.get(scored.tag)
        if not tag or not tag.active:
            continue
        assignment = ProductStyleTag(
            product_id=product.id,
            tag_id=tag.id,
            score=scored.score,
            model_version=result.model_version,
            classified_at=now,
        )
        db.add(assignment)
        assignments.append(assignment)
    db.flush()
    return assignments
