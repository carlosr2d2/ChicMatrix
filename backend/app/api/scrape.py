import logging

from celery import Celery
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies.auth import require_permission
from app.metrics import SCRAPE_TASKS
from app.models.models import Retailer, User
from app.schemas.schemas import ImageBackfillResponse, ScrapeResponse
from app.services.image_cache import iter_products_needing_image_cache

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["scraping"])

celery_app = Celery("chicmatrix")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_result_backend


@router.post("/images/backfill", response_model=ImageBackfillResponse)
def enqueue_image_backfill(
    retailer_id: int | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("admin:scrape")),
):
    if retailer_id is not None:
        retailer = db.query(Retailer).filter(Retailer.id == retailer_id).first()
        if not retailer:
            raise HTTPException(status_code=404, detail="Retailer not found")

    pending = len(
        iter_products_needing_image_cache(db, retailer_id=retailer_id, limit=limit)
    )

    result = celery_app.send_task(
        "workers.tasks.scraping.backfill_product_images",
        kwargs={"retailer_id": retailer_id, "limit": limit, "delay_ms": 50},
        queue="scraping",
    )

    SCRAPE_TASKS.labels(retailer_id=str(retailer_id or "all"), status="image_backfill").inc()
    logger.info(
        "Image backfill task enqueued by admin",
        extra={
            "task_id": result.id,
            "pending_estimate": pending,
            "retailer_id": retailer_id,
            "limit": limit,
            "admin_user_id": str(admin.id),
        },
    )

    scope = f"retailer {retailer_id}" if retailer_id is not None else "all retailers"
    return ImageBackfillResponse(
        task_id=result.id,
        status="enqueued",
        message=f"Image backfill queued for {scope} ({pending} pending, limit {limit})",
        pending_estimate=pending,
        retailer_id=retailer_id,
        limit=limit,
    )


@router.post("/{retailer_id}", response_model=ScrapeResponse)
def enqueue_scrape(
    retailer_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_permission("admin:scrape")),
):
    retailer = db.query(Retailer).filter(Retailer.id == retailer_id).first()
    if not retailer:
        raise HTTPException(status_code=404, detail="Retailer not found")
    if not retailer.is_active:
        raise HTTPException(status_code=400, detail="Retailer is inactive")

    result = celery_app.send_task(
        "workers.tasks.scraping.scrape_retailer",
        args=[retailer_id],
        queue="scraping",
    )

    SCRAPE_TASKS.labels(retailer_id=str(retailer_id), status="enqueued").inc()
    logger.info(
        "Scrape task enqueued by admin",
        extra={
            "retailer_id": retailer_id,
            "task_id": result.id,
            "admin_user_id": str(admin.id),
        },
    )

    return ScrapeResponse(
        retailer_id=retailer_id,
        task_id=result.id,
        status="enqueued",
        message=f"Scraping task queued for {retailer.name}",
    )
