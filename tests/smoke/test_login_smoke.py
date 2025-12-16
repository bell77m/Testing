"""
Smoke Tests - Critical Path Login Tests
รันก่อนทุกครั้งเพื่อตรวจสอบ core functionality
"""
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
import allure
from pages.login_page import LoginPage
from config.settings import BASE_URL


@allure.feature('Authentication')
@allure.story('Login')
@pytest.mark.smoke
class TestLoginSmoke:

    @allure.title('Verify successful login with valid credentials')
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_valid_credentials(self, page):
        """
        Test Case: TC_LOGIN_001
        Steps:
        1. Navigate to login page
        2. Enter valid username
        3. Enter valid password
        4. Click login button
        Expected: User redirected to dashboard
        """
        with allure.step('Navigate to login page'):
            login_page = LoginPage(page)
            login_page.navigate(f'{BASE_URL}/login')

        with allure.step('Enter valid credentials'):
            login_page.login('testuser@example.com', 'ValidPass123!')

        with allure.step('Verify successful login'):
            assert login_page.is_logged_in(), 'User should be logged in'
            assert page.url.endswith('/dashboard'), 'Should redirect to dashboard'


    @allure.title('Verify login fails with invalid credentials')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_invalid_credentials(self, page):
        """
        Test Case: TC_LOGIN_002
        Steps:
        1. Navigate to login page
        2. Enter invalid credentials
        3. Click login button
        Expected: Error message displayed
        """
        login_page = LoginPage(page)
        login_page.navigate(f'{BASE_URL}/login')

        with allure.step('Attempt login with invalid credentials'):
            login_page.login('invalid@example.com', 'WrongPassword')

        with allure.step('Verify error message'):
            error_msg = login_page.get_error_message()
            assert error_msg is not None, 'Error message should be displayed'
            assert 'invalid' in error_msg.lower(), f'Error message should mention invalid credentials: {error_msg}'


    @allure.title('Verify login page loads correctly')
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_login_page_loads(self, page):
        """
        Test Case: TC_LOGIN_003
        Verify all login page elements are visible
        """
        login_page = LoginPage(page)
        login_page.navigate(f'{BASE_URL}/login')

        with allure.step('Check page title'):
            assert 'Login' in page.title(), 'Page title should contain "Login"'

        with allure.step('Verify form elements are visible'):
            assert login_page.is_username_visible(), 'Username field should be visible'
            assert login_page.is_password_visible(), 'Password field should be visible'
            assert login_page.is_login_button_visible(), 'Login button should be visible'