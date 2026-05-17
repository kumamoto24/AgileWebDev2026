import pytest

selenium = pytest.importorskip("selenium")

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_logged_in_homepage_shows_search_and_recommendations(
    live_server_url,
    browser,
    logged_in_homepage_users,
):
    browser.get(live_server_url + "/")

    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "openLogin"))
    ).click()

    email_input = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email_input.send_keys(logged_in_homepage_users["email"])
    browser.find_element(By.ID, "password").send_keys(logged_in_homepage_users["password"])
    browser.find_element(By.CSS_SELECTOR, ".login-btn").click()

    WebDriverWait(browser, 5).until(EC.url_contains("/home"))

    welcome_heading = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".logged-home-hero h1"))
    )
    search_button = browser.find_element(By.XPATH, "//button[normalize-space()='Search']")
    recommended_profile = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Recommended Tester')]"))
    )

    assert browser.current_url.endswith("/home")
    assert welcome_heading.text == "Welcome back, Test Home User"
    assert search_button.is_displayed()
    assert recommended_profile.is_displayed()
