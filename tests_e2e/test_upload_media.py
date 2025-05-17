import time
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

BASE = "http://127.0.0.1:5000"

def test_upload_book(driver):
    driver.delete_all_cookies()  # Ensure session is cleared
    # Generate unique test user details
    unique_email = f"bookuser_{uuid.uuid4().hex[:6]}@example.com"
    unique_name = f"BookUser_{uuid.uuid4().hex[:6]}"
    password = "securepass123"

    #Sign up
    driver.get(f"{BASE}/signup")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "email")))
    driver.find_element(By.NAME, "full_name").send_keys(unique_name)
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    WebDriverWait(driver, 5).until(EC.url_contains("/login"))

    #Log in
    driver.find_element(By.NAME, "email").send_keys(unique_email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 5).until(EC.url_contains("/home"))

    #Upload a book
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "mediaType")))

    media_type_select = driver.find_element(By.ID, "mediaType")
    Select(media_type_select).select_by_value("book")

    # Trigger onchange event to show book-specific fields
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", media_type_select)

    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "bookFields")))
    driver.find_element(By.NAME, "title").send_keys("Selenium Book Upload")
    driver.find_element(By.NAME, "author").send_keys("Selenium Bot")
    Select(driver.find_element(By.NAME, "book_genre")).select_by_visible_text("Fiction")
    driver.execute_script("arguments[0].value = '2025-05-01'", driver.find_element(By.NAME, "date_started"))
    driver.execute_script("arguments[0].value = '2025-05-02'", driver.find_element(By.NAME, "date_finished"))

    Select(driver.find_element(By.NAME, "status")).select_by_visible_text("Finished")

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(1)
    submit_btn.click()

    #Verify uploaded entry appears
    driver.get(f"{BASE}/upload")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "upload-box")))

    page = driver.page_source
    
    assert "Selenium Book Upload" in page
    assert "Fiction" in page
