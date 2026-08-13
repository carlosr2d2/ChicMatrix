from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.models import Price, Product, ProductStyleTag, Retailer, StyleTag
from app.schemas.schemas import (
    LatestPrice,
    ProductListItem,
    ProductListResponse,
    ProductStyleTagOut,
)
from app.services.image_cache import absolute_image_url

router = APIRouter(prefix="/products", tags=["catalog"])


def _style_tags_out(product: Product) -> list[ProductStyleTagOut]:
    return [
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


def _latest_price(db: Session, product_id: int) -> LatestPrice | None:
    latest = (
        db.query(Price)
        .filter(Price.product_id == product_id)
        .order_by(Price.scraped_at.desc())
        .first()
    )
    if not latest:
        return None
    return LatestPrice(
        amount=latest.amount,
        currency=latest.currency,
        scraped_at=latest.scraped_at,
    )


def _to_list_item(
    product: Product,
    *,
    retailer_name: str | None,
    latest_price: LatestPrice | None,
) -> ProductListItem:
    return ProductListItem(
        id=product.id,
        name=product.name,
        description=product.description,
        image_url=absolute_image_url(product.image_url),
        product_url=product.product_url,
        category=product.category,
        brand=product.brand,
        color=product.color,
        retailer_id=product.retailer_id,
        retailer_name=retailer_name,
        latest_price=latest_price,
        style_tags=_style_tags_out(product),
    )


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

    items = [
        _to_list_item(
            product,
            retailer_name=retailers.get(product.retailer_id),
            latest_price=_latest_price(db, product.id),
        )
        for product in products
    ]
    return ProductListResponse(items=items, total=total)


@router.get("/{product_id}", response_model=ProductListItem)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.style_assignments).joinedload(ProductStyleTag.tag))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    retailer = db.query(Retailer).filter(Retailer.id == product.retailer_id).first()
    return _to_list_item(
        product,
        retailer_name=retailer.name if retailer else None,
        latest_price=_latest_price(db, product.id),
    )
