import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_signup_flow(driver):
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    unique_name = f"testuser_{uuid.uuid4().hex[:6]}"


    # Go to the signup page
    driver.get(f"{BASE}/signup")

    # Wait for the signup form (now using NAME instead of ID)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))

    # Fill the form using correct NAME fields
    driver.find_element(By.NAME, "full_name").send_keys(unique_name)
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys("securepass123")
    driver.find_element(By.NAME, "confirm_password").send_keys("securepass123")

    # Submit
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Wait for redirection to login
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    assert "/login" in driver.current_url
    assert "Login" in driver.page_source