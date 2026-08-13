"""Celery Beat schedule helpers (env-driven)."""

from __future__ import annotations

import os
from datetime import timedelta

from celery.schedules import crontab


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def build_beat_schedule() -> dict:
    """
    Build Celery beat_schedule from environment.

    Defaults (UTC):
      - scrape all active retailers daily at 06:00
      - image backfill daily at 07:00

    Override with:
      SCHEDULED_SCRAPES_ENABLED=true|false
      SCHEDULED_IMAGE_BACKFILL_ENABLED=true|false
      SCHEDULED_SCRAPE_HOUR_UTC / SCHEDULED_SCRAPE_MINUTE_UTC
      SCHEDULED_IMAGE_BACKFILL_HOUR_UTC / SCHEDULED_IMAGE_BACKFILL_MINUTE_UTC
      SCHEDULED_SCRAPE_INTERVAL_MINUTES (>0 replaces crontab with interval)
      SCHEDULED_IMAGE_BACKFILL_INTERVAL_MINUTES (>0 replaces crontab with interval)
    """
    schedule: dict = {}

    if _env_bool("SCHEDULED_SCRAPES_ENABLED", True):
        interval = _env_int("SCHEDULED_SCRAPE_INTERVAL_MINUTES", 0)
        if interval > 0:
            scrape_when = timedelta(minutes=interval)
        else:
            scrape_when = crontab(
                hour=_env_int("SCHEDULED_SCRAPE_HOUR_UTC", 6),
                minute=_env_int("SCHEDULED_SCRAPE_MINUTE_UTC", 0),
            )
        schedule["scrape-all-active-retailers"] = {
            "task": "workers.tasks.scraping.enqueue_active_retailer_scrapes",
            "schedule": scrape_when,
        }

    if _env_bool("SCHEDULED_IMAGE_BACKFILL_ENABLED", True):
        interval = _env_int("SCHEDULED_IMAGE_BACKFILL_INTERVAL_MINUTES", 0)
        if interval > 0:
            backfill_when = timedelta(minutes=interval)
        else:
            backfill_when = crontab(
                hour=_env_int("SCHEDULED_IMAGE_BACKFILL_HOUR_UTC", 7),
                minute=_env_int("SCHEDULED_IMAGE_BACKFILL_MINUTE_UTC", 0),
            )
        schedule["backfill-product-images"] = {
            "task": "workers.tasks.scraping.backfill_product_images",
            "schedule": backfill_when,
            "kwargs": {
                "limit": _env_int("SCHEDULED_IMAGE_BACKFILL_LIMIT", 500),
                "delay_ms": 50,
            },
        }

    return schedule
