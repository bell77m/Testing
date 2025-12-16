"""
Login Page Object Model
Contains all locators and methods for login page interactions
"""
from playwright.sync_api import Page, expect
from .base_page import BasePage
from utils.logger import get_logger, log_test_step

log = get_logger(__name__)


class LoginPage(BasePage):
    """Login page interactions and verifications"""

    # ==================== Locators ====================
    # Use data-testid for better stability, fallback to other selectors
    username_input = 'input[name="username"], input[name="email"], input[type="email"]'
    password_input = 'input[name="password"], input[type="password"]'
    login_button = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
    error_message = '.error-message, .alert-danger, [role="alert"]'
    forgot_password_link = 'a:has-text("Forgot"), a:has-text("Reset")'
    remember_me_checkbox = 'input[type="checkbox"][name*="remember"]'

    # Success indicators
    dashboard_url = '/dashboard'
    user_menu = '[data-testid="user-menu"], .user-profile, .avatar'


    # ==================== Actions ====================

    @log_test_step("Login with credentials")
    def login(self, username: str, password: str):
        """
        Perform login action

        Args:
            username: Username or email
            password: Password
        """
        try:
            log.info(f"Attempting login for user: {username}")

            self.page.fill(self.username_input, username)
            self.page.fill(self.password_input, password)
            self.page.click(self.login_button)

            # Wait for navigation or error
            self.page.wait_for_load_state('networkidle', timeout=5000)

        except Exception as e:
            log.error(f"Login failed: {str(e)}")
            raise


    def check_remember_me(self):
        """Check the 'Remember Me' checkbox"""
        log.debug("Checking remember me option")
        self.page.check(self.remember_me_checkbox)


    def click_forgot_password(self):
        """Click forgot password link"""
        log.debug("Clicking forgot password link")
        self.page.click(self.forgot_password_link)


    # ==================== Verifications ====================

    def is_logged_in(self) -> bool:
        """
        Check if user is logged in successfully

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check multiple indicators
            url_check = self.dashboard_url in self.page.url
            user_menu_visible = self.page.locator(self.user_menu).is_visible()

            return url_check or user_menu_visible

        except Exception as e:
            log.debug(f"Login check failed: {str(e)}")
            return False


    def get_error_message(self) -> str | None:
        """
        Get error message text if displayed

        Returns:
            Error message text or None
        """
        try:
            error_locator = self.page.locator(self.error_message)

            if error_locator.is_visible(timeout=2000):
                message = error_locator.text_content()
                log.debug(f"Error message found: {message}")
                return message

            return None

        except Exception as e:
            log.debug(f"No error message found: {str(e)}")
            return None


    def is_username_visible(self) -> bool:
        """Check if username field is visible"""
        return self.page.locator(self.username_input).is_visible()


    def is_password_visible(self) -> bool:
        """Check if password field is visible"""
        return self.page.locator(self.password_input).is_visible()


    def is_login_button_visible(self) -> bool:
        """Check if login button is visible"""
        return self.page.locator(self.login_button).is_visible()


    def is_forgot_password_visible(self) -> bool:
        """Check if forgot password link is visible"""
        return self.page.locator(self.forgot_password_link).is_visible()


    # ==================== Advanced Methods ====================

    @log_test_step("Quick login (direct navigation + login)")
    def quick_login(self, username: str, password: str, base_url: str):
        """
        Navigate to login page and perform login in one action

        Args:
            username: Username or email
            password: Password
            base_url: Base URL of the application
        """
        self.navigate(f"{base_url}/login")
        self.login(username, password)


    def wait_for_login_page_load(self):
        """Wait for login page to be fully loaded"""
        log.debug("Waiting for login page to load")
        self.page.wait_for_selector(self.username_input, state='visible')
        self.page.wait_for_selector(self.password_input, state='visible')
        self.page.wait_for_selector(self.login_button, state='visible')


    def get_password_field_type(self) -> str:
        """
        Get the type attribute of password field

        Returns:
            Field type (should be 'password' for security)
        """
        return self.page.locator(self.password_input).get_attribute('type')


    def clear_login_form(self):
        """Clear all login form fields"""
        log.debug("Clearing login form")
        self.page.fill(self.username_input, "")
        self.page.fill(self.password_input, "")


    # ==================== Playwright Assertions ====================

    def expect_login_success(self):
        """Assert that login was successful using Playwright expect"""
        expect(self.page).to_have_url(self.dashboard_url, timeout=5000)
        log.info("✓ Login successful - Redirected to dashboard")


    def expect_error_visible(self):
        """Assert that error message is visible"""
        expect(self.page.locator(self.error_message)).to_be_visible(timeout=3000)
        log.info("✓ Error message displayed as expected")