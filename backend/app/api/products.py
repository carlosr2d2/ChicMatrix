from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Price, Product, ProductStyleTag, Retailer, StyleTag
from app.schemas.schemas import (
    LatestPrice,
    ProductListItem,
    ProductListResponse,
    ProductStyleTagOut,
)

router = APIRouter(prefix="/products", tags=["catalog"])


@router.get("", response_model=ProductListResponse)
def list_products(
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    retailer_id: int | None = None,
    category: str | None = None,
    style: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if retailer_id is not None:
        query = query.filter(Product.retailer_id == retailer_id)
    if category:
        query = query.filter(Product.category.ilike(category))
    if style:
        query = (
            query.join(ProductStyleTag, ProductStyleTag.product_id == Product.id)
            .join(StyleTag, StyleTag.id == ProductStyleTag.tag_id)
            .filter(StyleTag.code == style.lower())
        )

    total = query.distinct().count() if style else query.count()
    products = (
        query.options(joinedload(Product.style_assignments).joinedload(ProductStyleTag.tag))
        .order_by(Product.updated_at.desc(), Product.id.desc())
        .offset(offset)
        .limit(limit)
        .distinct()
        .all()
    )

    retailer_ids = {p.retailer_id for p in products}
    retailers = {
        r.id: r.name
        for r in db.query(Retailer).filter(Retailer.id.in_(retailer_ids)).all()
    } if retailer_ids else {}

    items: list[ProductListItem] = []
    for product in products:
        latest = (
            db.query(Price)
            .filter(Price.product_id == product.id)
            .order_by(Price.scraped_at.desc())
            .first()
        )
        style_tags = [
            ProductStyleTagOut(
                code=assignment.tag.code,
                label_es=assignment.tag.label_es,
                score=assignment.score,
                model_version=assignment.model_version,
            )
            for assignment in sorted(
                product.style_assignments,
                key=lambda a: a.score,
                reverse=True,
            )
            if assignment.tag is not None
        ]
        items.append(
            ProductListItem(
                id=product.id,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
                product_url=product.product_url,
                category=product.category,
                brand=product.brand,
                color=product.color,
                retailer_id=product.retailer_id,
                retailer_name=retailers.get(product.retailer_id),
                latest_price=(
                    LatestPrice(
                        amount=latest.amount,
                        currency=latest.currency,
                        scraped_at=latest.scraped_at,
                    )
                    if latest
                    else None
                ),
                style_tags=style_tags,
            )
        )

    return ProductListResponse(items=items, total=total)
