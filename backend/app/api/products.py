from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Price, Product, Retailer
from app.schemas.schemas import LatestPrice, ProductListItem, ProductListResponse

router = APIRouter(prefix="/products", tags=["catalog"])


@router.get("", response_model=ProductListResponse)
def list_products(
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    retailer_id: int | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if retailer_id is not None:
        query = query.filter(Product.retailer_id == retailer_id)
    if category:
        query = query.filter(Product.category.ilike(category))

    total = query.count()
    products = (
        query.order_by(Product.updated_at.desc(), Product.id.desc())
        .offset(offset)
        .limit(limit)
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
        items.append(
            ProductListItem(
                id=product.id,
                name=product.name,
                description=product.description,
                image_url=product.image_url,
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
            )
        )

    return ProductListResponse(items=items, total=total)
