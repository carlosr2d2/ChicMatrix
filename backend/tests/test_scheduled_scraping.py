from datetime import timedelta

from celery.schedules import crontab

from app.models.models import Retailer
from app.services.beat_schedule import build_beat_schedule
from app.services.scheduled_scraping import enqueue_scrapes_for_active_retailers


def test_enqueue_scrapes_skips_inactive(db_session, sample_retailer):
    inactive = Retailer(
        name="Closed Shop",
        base_url="https://closed.demo",
        scraping_config={},
        is_active=False,
    )
    db_session.add(inactive)
    db_session.commit()

    seen: list[int] = []

    def enqueue_fn(retailer_id: int) -> str:
        seen.append(retailer_id)
        return f"task-{retailer_id}"

    result = enqueue_scrapes_for_active_retailers(db_session, enqueue_fn=enqueue_fn)

    assert result["enqueued"] == 1
    assert seen == [sample_retailer.id]
    assert result["tasks"][0]["task_id"] == f"task-{sample_retailer.id}"


def test_build_beat_schedule_defaults(monkeypatch):
    monkeypatch.delenv("SCHEDULED_SCRAPES_ENABLED", raising=False)
    monkeypatch.delenv("SCHEDULED_IMAGE_BACKFILL_ENABLED", raising=False)
    monkeypatch.delenv("SCHEDULED_SCRAPE_INTERVAL_MINUTES", raising=False)
    monkeypatch.delenv("SCHEDULED_IMAGE_BACKFILL_INTERVAL_MINUTES", raising=False)
    monkeypatch.delenv("SCHEDULED_IMAGE_BACKFILL_LIMIT", raising=False)
    monkeypatch.setenv("SCHEDULED_SCRAPE_HOUR_UTC", "6")
    monkeypatch.setenv("SCHEDULED_SCRAPE_MINUTE_UTC", "0")
    monkeypatch.setenv("SCHEDULED_IMAGE_BACKFILL_HOUR_UTC", "7")
    monkeypatch.setenv("SCHEDULED_IMAGE_BACKFILL_MINUTE_UTC", "0")

    schedule = build_beat_schedule()
    assert "scrape-all-active-retailers" in schedule
    assert "backfill-product-images" in schedule
    assert isinstance(schedule["scrape-all-active-retailers"]["schedule"], crontab)
    assert schedule["backfill-product-images"]["kwargs"]["limit"] == 500


def test_build_beat_schedule_interval_and_disable(monkeypatch):
    monkeypatch.setenv("SCHEDULED_SCRAPES_ENABLED", "true")
    monkeypatch.setenv("SCHEDULED_SCRAPE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("SCHEDULED_IMAGE_BACKFILL_ENABLED", "false")

    schedule = build_beat_schedule()
    assert "scrape-all-active-retailers" in schedule
    assert "backfill-product-images" not in schedule
    assert schedule["scrape-all-active-retailers"]["schedule"] == timedelta(minutes=15)
