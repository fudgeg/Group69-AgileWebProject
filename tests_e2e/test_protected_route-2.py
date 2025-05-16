from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

# Test for protected routes
# This test checks if the user is redirected to the login page when trying to access a protected route (/upload) without being logged in.
def test_upload_requires_login(driver):
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
    assert "Login" in driver.page_source