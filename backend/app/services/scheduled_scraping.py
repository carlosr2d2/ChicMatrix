"""Helpers for scheduled / bulk scrape enqueue (Celery Beat + admin)."""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from app.models.models import Retailer

logger = logging.getLogger(__name__)


def enqueue_scrapes_for_active_retailers(
    db: Session,
    *,
    enqueue_fn: Callable[[int], str],
) -> dict:
    """
    Queue a scrape for every active retailer via `enqueue_fn(retailer_id) -> task_id`.
    """
    retailers = (
        db.query(Retailer)
        .filter(Retailer.is_active.is_(True))
        .order_by(Retailer.id.asc())
        .all()
    )
    tasks = []
    for retailer in retailers:
        task_id = enqueue_fn(retailer.id)
        tasks.append(
            {
                "retailer_id": retailer.id,
                "name": retailer.name,
                "task_id": task_id,
            }
        )

    summary = {"enqueued": len(tasks), "tasks": tasks}
    logger.info("Enqueued scrapes for active retailers", extra=summary)
    return summary
