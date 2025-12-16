import sys
from pathlib import Path

# Add project root to Python path (works everywhere)
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"✅ Project root added to path: {project_root}")

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function")
def setup(page: Page):
    """
    Setup fixture for each test

    Args:
        page: Playwright page instance

    Yields:
        Configured page object
    """
    # Setup code here
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.set_default_timeout(5000)

    yield page

    # Teardown code here
    # page.context.clear_cookies()  # If needed


@pytest.fixture(scope="session", autouse=True)
def verify_imports():
    """Verify that imports are working"""
    try:
        from pages.login_page import LoginPage
        from config.settings import BASE_URL
        print("✅ All imports working correctly!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        raise