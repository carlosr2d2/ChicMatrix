# Official Playwright image includes Chromium and all system dependencies.
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY workers/requirements.txt ./workers/
RUN pip install --no-cache-dir -r workers/requirements.txt

COPY backend/ ./backend/
COPY workers/ ./workers/

ENV PYTHONPATH=/app/backend:/app
ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "-Q", "scraping", "-c", "4"]
