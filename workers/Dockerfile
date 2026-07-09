FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY workers/requirements.txt ./workers/
RUN pip install --no-cache-dir -r workers/requirements.txt \
    && playwright install --with-deps chromium

COPY backend/ ./backend/
COPY workers/ ./workers/

ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "-Q", "scraping", "-c", "4"]
