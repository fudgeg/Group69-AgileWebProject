import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_login_logout(driver):
    # 1) Go to the login page
    driver.get(f"{BASE}/login")

    # 2) Wait for the form to appear
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )

    # 3) Verify inputs exist
    assert driver.find_element(By.NAME, "email")
    assert driver.find_element(By.NAME, "password")

    # 4) Enter Alice’s credentials and submit
    driver.find_element(By.NAME, "email").send_keys("alice@example.com")
    driver.find_element(By.NAME, "password").send_keys("test123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 5) Wait until /home loads
    WebDriverWait(driver, 5).until(
        EC.url_contains("/home")
    )
    assert "/home" in driver.current_url
    assert "Soul Maps" in driver.page_source

    # 6) Now log out
    driver.get(f"{BASE}/logout")

    # 7) Wait for the login page to load
    WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Soul Maps')]"))
)


    # 8) Confirm we’re back at the root URL
    assert driver.current_url.rstrip("/") == BASE
