# """
# Regression Tests - Comprehensive Login Test Suite
# ครอบคลุมทุก scenario รวมถึง edge cases
# """
# import sys
# from pathlib import Path
#
# # Fix import path
# sys.path.insert(0, str(Path(__file__).parent.parent.parent))
#
# import pytest
# import allure
# from pages.login_page import LoginPage
# from config.settings import BASE_URL
#
#
# @allure.feature('Authentication')
# @allure.story('Login - Full Coverage')
# @pytest.mark.regression
# class TestLoginFull:
#
#     # ==================== Positive Tests ====================
#
#     @allure.title('Login with email format username')
#     @allure.severity(allure.severity_level.NORMAL)
#     def test_login_with_email(self, page):
#         """TC_LOGIN_004: Verify login with email format"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#         login_page.login('user@example.com', 'ValidPass123!')
#         assert login_page.is_logged_in()
#
#     @allure.title('Login with remember me option')
#     @allure.severity(allure.severity_level.NORMAL)
#     def test_login_with_remember_me(self, page):
#         """TC_LOGIN_005: Verify remember me checkbox functionality"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#         login_page.check_remember_me()
#         login_page.login('testuser@example.com', 'ValidPass123!')
#         assert login_page.is_logged_in()
#         # TODO: Verify session persistence after browser restart
#
#     # ==================== Negative Tests ====================
#
#     @allure.title('Login with empty credentials')
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.parametrize('username,password,expected_error', [
#         ('', '', 'required'),
#         ('user@example.com', '', 'password'),
#         ('', 'ValidPass123!', 'username'),
#     ])
#     def test_login_empty_fields(self, page, username, password, expected_error):
#         """TC_LOGIN_006: Verify validation for empty fields"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#         login_page.login(username, password)
#
#         error_msg = login_page.get_error_message()
#         assert error_msg is not None
#         assert expected_error.lower() in error_msg.lower()
#
#     @allure.title('Login with special characters in password')
#     @allure.severity(allure.severity_level.NORMAL)
#     def test_login_special_chars_password(self, page):
#         """TC_LOGIN_007: Verify special characters in password are handled"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#         login_page.login('testuser@example.com', 'P@$$w0rd!#%&*()')
#         # Should either login successfully or show appropriate error
#         assert page.url != f'{BASE_URL}/login' or login_page.get_error_message()
#
#     @allure.title('Login with SQL injection attempt')
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.security
#     def test_login_sql_injection(self, page):
#         """TC_LOGIN_008: Security test - SQL injection prevention"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         sql_payloads = [
#             "' OR '1'='1",
#             "admin'--",
#             "' OR '1'='1' /*",
#         ]
#
#         for payload in sql_payloads:
#             with allure.step(f'Testing payload: {payload}'):
#                 login_page.login(payload, payload)
#                 assert not login_page.is_logged_in(), f'Should not login with SQL injection: {payload}'
#                 login_page.navigate(f'{BASE_URL}/login')  # Reset
#
#     @allure.title('Login with XSS attempt')
#     @allure.severity(allure.severity_level.CRITICAL)
#     @pytest.mark.security
#     def test_login_xss_attempt(self, page):
#         """TC_LOGIN_009: Security test - XSS prevention"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         xss_payload = '<script>alert("XSS")</script>'
#         login_page.login(xss_payload, 'password')
#
#         # Verify no alert dialog appears
#         assert not page.evaluate('window.alert') or len(page.context.pages) == 1
#
#     # ==================== Rate Limiting Tests ====================
#
#     @allure.title('Login rate limiting after multiple failed attempts')
#     @allure.severity(allure.severity_level.NORMAL)
#     @pytest.mark.slow
#     def test_login_rate_limiting(self, page):
#         """TC_LOGIN_010: Verify account lockout after failed attempts"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         # Attempt login 5 times with wrong password
#         for i in range(5):
#             with allure.step(f'Failed login attempt {i + 1}'):
#                 login_page.login('testuser@example.com', 'WrongPassword')
#
#         # 6th attempt should show lockout message
#         with allure.step('Verify account lockout'):
#             login_page.login('testuser@example.com', 'WrongPassword')
#             error = login_page.get_error_message()
#             assert 'locked' in error.lower() or 'many attempts' in error.lower()
#
#     # ==================== UI/UX Tests ====================
#
#     @allure.title('Password field should mask input')
#     @allure.severity(allure.severity_level.MINOR)
#     def test_password_field_masked(self, page):
#         """TC_LOGIN_011: Verify password field has type='password'"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         password_field = page.locator(login_page.password_input)
#         input_type = password_field.get_attribute('type')
#         assert input_type == 'password', 'Password field should be masked'
#
#     @allure.title('Forgot password link is visible and clickable')
#     @allure.severity(allure.severity_level.MINOR)
#     def test_forgot_password_link(self, page):
#         """TC_LOGIN_012: Verify forgot password link functionality"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         assert login_page.is_forgot_password_visible()
#         login_page.click_forgot_password()
#         assert 'forgot' in page.url.lower() or 'reset' in page.url.lower()
#
#     # ==================== Accessibility Tests ====================
#
#     @allure.title('Login form should have proper labels')
#     @allure.severity(allure.severity_level.MINOR)
#     @pytest.mark.accessibility
#     def test_login_form_labels(self, page):
#         """TC_LOGIN_013: Verify form accessibility"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         # Check for labels
#         username_label = page.locator('label[for*="username"], label[for*="email"]')
#         password_label = page.locator('label[for*="password"]')
#
#         assert username_label.count() > 0, 'Username field should have a label'
#         assert password_label.count() > 0, 'Password field should have a label'
#
#     # ==================== Browser Compatibility ====================
#
#     @allure.title('Login works with autofill')
#     @allure.severity(allure.severity_level.MINOR)
#     def test_login_with_autofill(self, page):
#         """TC_LOGIN_014: Verify login form supports browser autofill"""
#         login_page = LoginPage(page)
#         login_page.navigate(f'{BASE_URL}/login')
#
#         # Check autocomplete attributes
#         username_field = page.locator(login_page.username_input)
#         username_autocomplete = username_field.get_attribute('autocomplete')
#
#         assert username_autocomplete in ['username', 'email', 'on', None], \
#             'Username field should allow autocomplete'



import pytest
import allure
from playwright.sync_api import Page, expect

@allure.feature('Authentication')
@allure.story('Login - Full Coverage')
@pytest.mark.regression
class TestLoginFull:

    @allure.title('Check navigate error message')
    @allure.severity(allure.severity_level.NORMAL)
    # แก้ไข: เติม self เป็น argument ตัวแรก
    def test_regression_login_locked_out(self, page: Page):
        with allure.step("Open login page"):
            page.goto("https://www.saucedemo.com/")

        with allure.step("Login with locked_out user"):
            # ใช้ User ที่ถูกล็อค
            page.fill("#user-name", "locked_out_user")
            page.fill("#password", "secret_sauce")
            page.click("#login-button")
        with allure.step("Verify error message"):
            # ต้องเจอ Error Message สีแดง
            error_msg = page.locator("[data-test='error']")
            expect(error_msg).to_be_visible()
            expect(error_msg).to_contain_text("Sorry, this user has been locked out.")
