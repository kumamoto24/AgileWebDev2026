import threading
from uuid import uuid4
from unittest.mock import patch

import pytest
from werkzeug.serving import make_server

selenium = pytest.importorskip("selenium")

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import app


@pytest.fixture(scope="module")
def live_server_url():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        RECAPTCHA_SITE_KEY="test-site-key",
        RECAPTCHA_SECRET_KEY="test-secret-key",
    )

    try:
        server = make_server("127.0.0.1", 0, app)
    except SystemExit:
        pytest.skip("Local test server cannot bind to a port in this environment.")
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    yield f"http://127.0.0.1:{server.server_port}"

    server.shutdown()
    server_thread.join(timeout=5)


@pytest.fixture()
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")

    try:
        driver = webdriver.Chrome(options=options)
    except WebDriverException as error:
        pytest.skip(f"Chrome WebDriver is not available: {error}")

    yield driver

    driver.quit()


def test_signup_page_renders_and_accepts_new_user(live_server_url, browser):
    #generates a random unique string.
    unique_id = uuid4().hex
    new_email = f"signup-{unique_id}@example.com"
    new_password = "Password123"

    browser.get(live_server_url + "/signup")

    email_input = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    password_input = browser.find_element(By.ID, "password")
    confirm_input = browser.find_element(By.ID, "confirm_password")
    submit_button = browser.find_element(By.CSS_SELECTOR, ".login-btn")

    #javascript to bypass reCAPTCHA since we can't solve it in tests
    browser.execute_script(
        "const token=document.createElement('input');"
        "token.type='hidden';"
        "token.name='g-recaptcha-response';"
        "token.value='test-captcha';"
        "document.querySelector('.signup-form').appendChild(token);"
    )

    #NB:the mocking ggogle API request 
    #it replaces the actual call to Google's reCAPTCHA verification endpoint with a mock that always returns success.
    with patch("app.routes.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"success": True}
        #Above is the recaptcha verification response that the app expects to receive from Google's API when the reCAPTCHA is successfully solved.
        email_input.send_keys(new_email)
        password_input.send_keys(new_password)
        confirm_input.send_keys(new_password)
        submit_button.click()

        #waits for redirection to profile page after successful signup
        WebDriverWait(browser, 5).until(EC.url_contains("/profile"))

    assert browser.current_url.endswith("/profile")
    display_name = browser.find_element(By.ID, "displayName")
    edit_button = browser.find_element(By.ID, "editProfileBtn")

    assert display_name.text in ["New Member", ""]
    assert edit_button.is_displayed()
