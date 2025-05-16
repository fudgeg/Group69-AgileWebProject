from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_home_requires_login(driver):
    driver.get(f"{BASE}/home")
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
    assert "Login" in driver.page_source

def test_upload_requires_login(driver):
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
    assert "Login" in driver.page_source