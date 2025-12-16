"""
Base Page Object Model
Parent class for all page objects with common methods
"""
from playwright.sync_api import Page
from utils.logger import get_logger

log = get_logger(__name__)


class BasePage:
    """Base page with common functionality for all pages"""

    def __init__(self, page: Page):
        """
        Initialize base page

        Args:
            page: Playwright Page instance
        """
        self.page = page

    def navigate(self, url: str):
        """
        Navigate to a URL

        Args:
            url: URL to navigate to
        """
        log.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until='domcontentloaded')

    def get_title(self) -> str:
        """
        Get page title

        Returns:
            Page title
        """
        return self.page.title()

    def get_url(self) -> str:
        """
        Get current URL

        Returns:
            Current page URL
        """
        return self.page.url

    def wait_for_selector(self, selector: str, timeout: int = 5000):
        """
        Wait for element to be visible

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        log.debug(f"Waiting for selector: {selector}")
        self.page.wait_for_selector(selector, state='visible', timeout=timeout)

    def click(self, selector: str):
        """
        Click an element

        Args:
            selector: CSS selector
        """
        log.debug(f"Clicking: {selector}")
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        """
        Fill input field

        Args:
            selector: CSS selector
            text: Text to fill
        """
        log.debug(f"Filling {selector} with: {text}")
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """
        Get text content of element

        Args:
            selector: CSS selector

        Returns:
            Text content
        """
        return self.page.locator(selector).text_content()

    def is_visible(self, selector: str) -> bool:
        """
        Check if element is visible

        Args:
            selector: CSS selector

        Returns:
            True if visible, False otherwise
        """
        try:
            return self.page.locator(selector).is_visible(timeout=2000)
        except:
            return False

    def take_screenshot(self, filename: str):
        """
        Take screenshot of current page

        Args:
            filename: Screenshot filename
        """
        log.info(f"Taking screenshot: {filename}")
        self.page.screenshot(path=filename)

    def reload(self):
        """Reload current page"""
        log.debug("Reloading page")
        self.page.reload()

    def go_back(self):
        """Navigate back"""
        log.debug("Navigating back")
        self.page.go_back()

    def wait_for_load_state(self, state: str = 'load'):
        """
        Wait for page load state

        Args:
            state: Load state ('load', 'domcontentloaded', 'networkidle')
        """
        log.debug(f"Waiting for load state: {state}")
        self.page.wait_for_load_state(state)