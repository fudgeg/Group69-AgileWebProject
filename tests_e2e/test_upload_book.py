import time
import uuid
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_upload_book(driver):
    unique_email = f"bookuser_{uuid.uuid4().hex[:6]}@example.com"
    unique_name = f"BookUser_{uuid.uuid4().hex[:6]}"
    password = "securepass123"

    # Step 1: Signup
    driver.get(f"{BASE}/signup")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
    driver.find_element(By.NAME, "full_name").send_keys(unique_name)
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))

    # Step 2: Login
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/home"))

    # Step 3: Upload Book
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "mediaType")))
    Select(driver.find_element(By.ID, "mediaType")).select_by_value("book")

    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "author")))
    driver.find_element(By.NAME, "title").send_keys("Selenium Book Upload")
    driver.find_element(By.NAME, "author").send_keys("Selenium Bot")
    Select(driver.find_element(By.NAME, "book_genre")).select_by_visible_text("Fiction")
    driver.find_element(By.NAME, "date_started").send_keys("2025-05-01")
    driver.find_element(By.NAME, "date_finished").send_keys("2025-05-02")
    Select(driver.find_element(By.NAME, "status")).select_by_visible_text("Finished")

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(1)
    submit_btn.click()
    time.sleep(1)
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "upload-box")))
    print("[DEBUG] Upload page source:\n", driver.page_source[:1000])  # First 1000 chars

    # Step 4: Revisit Upload Page to Verify Entry
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(
    EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Selenium Book Upload")
)

    page = driver.page_source

    print("[DEBUG] Verifying uploaded book is in the page...")
    assert "Selenium Book Upload" in driver.page_source
    assert "Fiction" in driver.page_source
