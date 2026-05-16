import threading

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


def test_homepage_hero_is_visible_in_browser(live_server_url, browser):
    browser.get(live_server_url + "/")

    hero_heading = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".hero-section h1"))
    )
    signup_link = browser.find_element(By.LINK_TEXT, "Get Started")

    assert "HeartLink" in browser.title
    assert hero_heading.text == "Find Your Perfect Match"
    assert signup_link.get_attribute("href").endswith("/signup")
