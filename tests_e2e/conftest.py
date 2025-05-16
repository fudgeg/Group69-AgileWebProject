import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# This fixture sets up the Chrome WebDriver for Selenium tests.
# It installs the ChromeDriver using webdriver_manager and launches it in headless mode.
# After the tests are done, it quits the driver to free up resources.
@pytest.fixture(scope="session")
def driver():
    # install & launch ChromeDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")            # no browser UI
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()
