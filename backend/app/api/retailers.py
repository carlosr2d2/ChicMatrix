from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Retailer
from app.schemas.schemas import RetailerListResponse, RetailerResponse

router = APIRouter(prefix="/retailers", tags=["catalog"])


@router.get("", response_model=RetailerListResponse)
def list_retailers(
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    query = db.query(Retailer)
    if active_only:
        query = query.filter(Retailer.is_active.is_(True))

    retailers = query.order_by(Retailer.name.asc()).all()
    items = [RetailerResponse.model_validate(r) for r in retailers]
    return RetailerListResponse(items=items, total=len(items))
