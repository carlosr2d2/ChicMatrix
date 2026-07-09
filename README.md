# ChicMatrix

Personalized fashion platform with price scraping, built with FastAPI, Next.js, PostgreSQL, Redis, and Celery.

## Architecture

```
Frontend (Next.js) -> Backend (FastAPI) -> PostgreSQL
                         |
                    Redis <-> Celery Workers
                         |
              Flower / Prometheus / Grafana
```

## Quick start

```bash
docker compose up --build
```

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost:3002        |
| API        | http://localhost:8001        |
| API Docs   | http://localhost:8001/docs   |
| Flower     | http://localhost:5556        |
| Prometheus | http://localhost:9090        |
| Grafana    | http://localhost:3001        |

Grafana credentials: `admin` / `chicmatrix`

## API endpoints

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/health`                 | Service health check           |
| POST   | `/scrape/{retailer_id}`   | Enqueue scraping task          |
| GET    | `/recommend/{user_id}`    | Personalized recommendations   |
| GET    | `/metrics`                | Prometheus metrics             |

## Example usage

```bash
curl http://localhost:8001/health
curl -X POST http://localhost:8001/scrape/1
curl http://localhost:8001/recommend/1
```

## Testing

### Backend (Pytest)

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
pytest -v
```

### Frontend (Jest)

```bash
cd frontend
npm install
npm test
```

## Playwright scraping

For JavaScript-heavy retailer sites, set `engine: "playwright"` in `retailers.scraping_config`:

```json
{
  "engine": "playwright",
  "listing_url": "https://shop.example.com/new-in",
  "wait_selector": ".product-card",
  "wait_until": "networkidle",
  "timeout_ms": 30000,
  "selectors": {
    "item": ".product-card",
    "name": ".product-title",
    "price": "[data-price]"
  }
}
```

## CI/CD

GitHub Actions runs backend tests (Pytest + Playwright), frontend tests (Jest), and Docker builds on every push/PR (`.github/workflows/ci.yml`).

## Scaling workers

```bash
docker compose up --build --scale worker=4
```
