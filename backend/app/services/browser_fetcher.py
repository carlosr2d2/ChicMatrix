import logging

logger = logging.getLogger(__name__)


class PlaywrightFetcher:
    """Fetches rendered HTML from JavaScript-heavy retailer pages."""

    def fetch_html(self, url: str, config: dict) -> str:
        from playwright.sync_api import sync_playwright

        timeout = config.get("timeout_ms", 30000)
        wait_selector = config.get("wait_selector")
        wait_until = config.get("wait_until", "networkidle")
        user_agent = config.get("headers", {}).get("User-Agent")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent) if user_agent else browser.new_context()
            page = context.new_page()
            try:
                page.goto(url, wait_until=wait_until, timeout=timeout)
                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=timeout)
                return page.content()
            finally:
                context.close()
                browser.close()

    @staticmethod
    def is_available() -> bool:
        try:
            import playwright  # noqa: F401
            return True
        except ImportError:
            return False
