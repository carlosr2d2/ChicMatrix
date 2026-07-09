import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.scraping import ScrapingService
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

database_url = os.getenv(
    "DATABASE_URL", "postgresql://chicmatrix:chicmatrix@db:5432/chicmatrix"
)
engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task(name="workers.tasks.scraping.scrape_retailer", bind=True, max_retries=3)
def scrape_retailer(self, retailer_id: int):
    db = SessionLocal()
    try:
        service = ScrapingService(db)
        result = service.scrape_retailer(retailer_id)
        logger.info("Scrape task finished", extra={"retailer_id": retailer_id, **result})
        return result
    except Exception as exc:
        logger.exception("Scrape task failed", extra={"retailer_id": retailer_id})
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
