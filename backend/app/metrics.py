from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "chicmatrix_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "chicmatrix_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

SCRAPE_TASKS = Counter(
    "chicmatrix_scrape_tasks_total",
    "Scraping tasks enqueued",
    ["retailer_id", "status"],
)

RECOMMENDATIONS = Counter(
    "chicmatrix_recommendations_total",
    "Recommendation requests",
    ["user_id"],
)


def metrics_response():
    return generate_latest(), CONTENT_TYPE_LATEST
