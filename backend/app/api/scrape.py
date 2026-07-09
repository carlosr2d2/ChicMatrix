import logging

from celery import Celery
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.metrics import SCRAPE_TASKS
from app.models.models import Retailer
from app.schemas.schemas import ScrapeResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["scraping"])

celery_app = Celery("chicmatrix")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_result_backend


@router.post("/{retailer_id}", response_model=ScrapeResponse)
def enqueue_scrape(retailer_id: int, db: Session = Depends(get_db)):
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
        "Scrape task enqueued",
        extra={"retailer_id": retailer_id, "task_id": result.id},
    )

    return ScrapeResponse(
        retailer_id=retailer_id,
        task_id=result.id,
        status="enqueued",
        message=f"Scraping task queued for {retailer.name}",
    )
