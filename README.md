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

Product data flow (scrapes are **admin-only**, customers only read):

```
Admin UI / POST /scrape/{id}
        → Redis queue
        → Celery worker (fixture or HTTP/Playwright)
        → products + prices
Customers → GET /products, PATCH profile, GET /recommend/me
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

## Seed accounts

| Email | Password | Role |
|-------|----------|------|
| `demo@chicmatrix.app` | `DemoPass123` | customer |
| `admin@chicmatrix.app` | `AdminPass123` | admin (`admin:scrape`) |

## Product loop (E2E)

Use this path to verify the full system after `docker compose up --build`:

1. **Health** — `curl http://localhost:8001/health` → `{"status":"ok",...}`
2. **Admin scrape** — login as `admin@chicmatrix.app` → [http://localhost:3002/admin](http://localhost:3002/admin) → enqueue Maison Noir / Urban Loom / Atelier Vue
3. **Worker** — Flower [http://localhost:5556](http://localhost:5556) → tasks `SUCCESS`
4. **Catalog** — home [http://localhost:3002](http://localhost:3002) → Featured pieces show names, images, prices (`GET /products`)
5. **Customer profile** — login as `demo@chicmatrix.app` → [http://localhost:3002/profile](http://localhost:3002/profile) → save colors/brands/occasions
6. **Recommendations** — [http://localhost:3002/recommendations](http://localhost:3002/recommendations) → ranked picks with match score, reasons, best price

Customers never trigger scrapes. Only admins enqueue work; workers write the catalog.

### System-ready checklist

- [ ] `docker compose ps` — backend, frontend, worker, db, redis healthy
- [ ] `/health` returns ok
- [ ] At least one scrape task SUCCEEDED in Flower
- [ ] `GET /products` returns items with `latest_price` and `image_url`
- [ ] Demo user can open `/profile` and save preferences
- [ ] `/recommendations` shows scored items (or a clear empty state if catalog is empty)
- [ ] Non-admin cannot `POST /scrape/{id}` (403)
- [ ] Backend `pytest` and frontend `npm test` pass

## API endpoints

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/health`                 | Service health check           |
| GET    | `/products`               | Catalog from scraped products  |
| GET    | `/retailers`              | Active retailers               |
| POST   | `/scrape/{retailer_id}`   | Enqueue scrape (**admin only**) |
| GET    | `/recommend/me`           | Recommendations for JWT user   |
| GET    | `/recommend/{user_id}`    | Recommendations by user UUID   |
| PATCH  | `/users/me/profile`       | Update fashion profile         |
| GET    | `/users/me`               | Current user fashion profile   |
| GET    | `/metrics`                | Prometheus metrics             |

### UI routes

| Path | Who | Purpose |
|------|-----|---------|
| `/` | public | Live catalog |
| `/login` `/register` | public | Auth |
| `/dashboard` | logged-in | Account + CTAs |
| `/profile` | logged-in | Fashion profile |
| `/recommendations` | logged-in | Personalized picks |
| `/admin` | admin | Enqueue scrapes |

## Example usage

```bash
curl http://localhost:8001/health

# Login (email method)
curl -X POST http://localhost:8001/login \
  -H "Content-Type: application/json" \
  -d '{"method":"email","email":"admin@chicmatrix.app","password":"AdminPass123"}'

curl -X POST http://localhost:8001/scrape/1 -H "Authorization: Bearer <admin_token>"
curl http://localhost:8001/products
curl http://localhost:8001/recommend/me -H "Authorization: Bearer <demo_token>"
```

## Testing

### Backend (Pytest)

```bash
# Local
cd backend && pip install -r requirements.txt && playwright install chromium && pytest -v

# Or inside Docker
docker compose exec backend pytest -v
```

Coverage for the product loop includes catalog/profile/recommend (`tests/test_catalog_and_profile.py`), admin scrape auth (`tests/test_api.py`), and fixture scraping (`tests/test_scraping.py`).

### Frontend (Jest)

```bash
cd frontend
npm install
npm test
# CI-style:
npm run test:ci
```

Jest covers `CatalogGrid`, `RecommendationsGrid`, `ProfileForm`, and API client helpers.

## Demo-safe scraping fixtures

Seed retailers scrape **local HTML fixtures** (not live storefronts), so the pipeline stays offline-friendly:

| Retailer | `listing_url` |
|----------|---------------|
| Maison Noir | `fixture://maison_noir.html` |
| Urban Loom | `fixture://urban_loom.html` |
| Atelier Vue | `fixture://atelier_vue.html` |

### Live HTTP retailer (Practice Boutique)

A fourth seeded retailer hits a **public practice fashion catalog** over real HTTP (admin-only, single listing page):

| Field | Value |
|-------|--------|
| Name | Practice Boutique |
| URL | `https://automationexercise.com/products` |
| Engine | `httpx` |
| Politeness | `request_delay_ms` + identifying `User-Agent` |
| Enrichment | Optional PDP fetch (`enrich_product_details`) for brand/category text |

Offline CI uses the same DOM snapshot: `fixture://automation_exercise_products.html`.

Fixtures live in `backend/fixtures/scraping/`. The worker parses them with the same BeautifulSoup selectors used for real HTTP pages, including **description** and **product URL**, then runs the **style classifier** (default **hybrid** = F0 lexicon first, F1 NLP fallback) into `style_tags` / `product_style_tags`.

Closed style vocabulary v1: `formal`, `sport`, `biker`, `rocker`, `casual`, `minimal`, `streetwear`.

Filter catalog by style: `GET /products?style=formal`.

Set `STYLE_CLASSIFIER_MODE=f0|f1|hybrid` (default `hybrid`).

## Style classifier evaluation (F0 / F1)

Frozen gold set (397 labeled products) lives in `backend/fixtures/style_gold/gold_set.jsonl`. Labels are multi-label against the closed vocabulary.

| Subset | Role |
|--------|------|
| `lexicon` | Wording F0 should catch (regression floor) |
| `paraphrase` | Human-true styles with synonyms F0 may miss |
| `overlap` | Multi-label (e.g. biker+rocker) |
| `negative` | No style tags |

```bash
docker compose exec backend python -m app.services.style_eval --mode f0
docker compose exec backend python -m app.services.style_eval --mode hybrid
# or locally: cd backend && PYTHONPATH=. python -m app.services.style_eval --mode hybrid
```

**F0 baseline** (`rules-v1`, `backend/fixtures/style_gold/f0_baseline.json`): micro-F1 **0.86**, lexicon F1 **1.00**, paraphrase F1 **0.13**.

**F1** (`nlp-tfidf-v1`): pure-Python TF-IDF centroids trained on the gold set (`backend/fixtures/style_models/f1_tfidf_v1.json`).

**Hybrid** (`hybrid-f0-f1-v1`, production default): F0-first; F1 only when F0 returns no tags — keeps lexicon precision **1.0** and lifts paraphrase F1 to **~0.92** on the full gold set. Honest hold-out (F1 trained without paraphrase): paraphrase F1 **~0.63** (still a large jump vs F0). Snapshot: `backend/fixtures/style_gold/f1_baseline.json`.

Retrain F1 after gold/taxonomy changes:

```bash
cd backend && PYTHONPATH=. python scripts/train_style_f1.py
```

Regenerate the gold file only if the taxonomy changes: `cd backend && python scripts/generate_style_gold.py`.

```json
{
  "engine": "httpx",
  "listing_url": "fixture://maison_noir.html",
  "currency": "USD",
  "selectors": {
    "item": "article.product",
    "name": ".product-title",
    "price": ".price",
    "color": ".color"
  }
}
```

Supported local sources: `fixture://file.html`, optional `fixture` config key, or `file:///...` paths. Override the fixtures directory with `SCRAPING_FIXTURES_DIR`.

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
