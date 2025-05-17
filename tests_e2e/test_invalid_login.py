from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_invalid_login(driver):
    driver.delete_all_cookies()  # Ensure session is cleared
    driver.get(f"{BASE}/login")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))

    driver.find_element(By.NAME, "email").send_keys("nonexistent@example.com")
    driver.find_element(By.NAME, "password").send_keys("wrongpass")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".popup-message.error")))
    assert "Invalid email or password" in driver.page_source