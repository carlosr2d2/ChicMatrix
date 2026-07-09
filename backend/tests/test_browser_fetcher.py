import pytest
from unittest.mock import MagicMock, patch

from app.services.browser_fetcher import PlaywrightFetcher


def test_playwright_fetcher_returns_page_content():
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><article class='product'>...</article></html>"

    mock_context = MagicMock()
    mock_context.new_page.return_value = mock_page

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = mock_context

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_playwright
    mock_cm.__exit__.return_value = None

    with patch("playwright.sync_api.sync_playwright", return_value=mock_cm):
        html = PlaywrightFetcher().fetch_html(
            "https://shop.example.com/catalog",
            {"wait_selector": ".product-card", "timeout_ms": 5000},
        )

    assert "product" in html
    mock_page.goto.assert_called_once()
    mock_page.wait_for_selector.assert_called_once_with(".product-card", timeout=5000)


@pytest.mark.playwright
def test_playwright_fetcher_integration():
    pytest.importorskip("playwright")
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
    except PlaywrightError as exc:
        pytest.skip(f"Chromium not available: {exc}")

    fetcher = PlaywrightFetcher()
    html = fetcher.fetch_html(
        "data:text/html,<html><body><article class='product'><h3>Coat</h3></article></body></html>",
        {"wait_until": "load"},
    )
    assert "Coat" in html
