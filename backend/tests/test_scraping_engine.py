from unittest.mock import patch

from app.services.scraping import ScrapingService


def test_fetch_html_uses_playwright_when_configured():
    service = ScrapingService(db=None)
    html = "<html><body>playwright</body></html>"

    with patch.object(
        ScrapingService,
        "_fetch_html",
        wraps=service._fetch_html,
    ):
        with patch("app.services.scraping.PlaywrightFetcher") as fetcher_cls:
            fetcher_cls.is_available.return_value = True
            fetcher_cls.return_value.fetch_html.return_value = html

            result = service._fetch_html(
                "https://dynamic-shop.demo/catalog",
                {"engine": "playwright", "wait_selector": ".product-card"},
                {"User-Agent": "ChicMatrixBot/1.0"},
            )

    assert "playwright" in result
    fetcher_cls.return_value.fetch_html.assert_called_once()


def test_fetch_html_playwright_missing_raises():
    service = ScrapingService(db=None)

    with patch("app.services.scraping.PlaywrightFetcher") as fetcher_cls:
        fetcher_cls.is_available.return_value = False
        try:
            service._fetch_html(
                "https://dynamic-shop.demo",
                {"engine": "playwright"},
                {},
            )
            raised = False
        except RuntimeError as exc:
            raised = True
            assert "Playwright is not installed" in str(exc)

    assert raised
