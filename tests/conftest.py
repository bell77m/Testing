import pytest
from playwright.sync_api import Page

@pytest.fixture(scope="function")
def setup(page: Page):
    # Setup code here
    yield page