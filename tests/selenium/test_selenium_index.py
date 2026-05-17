import threading
from uuid import uuid4

import pytest
from werkzeug.serving import make_server

selenium = pytest.importorskip("selenium")

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import app, db
from app.models import Interest, Profile, User


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


# This test creates a complete test user and profile, then tests the login and logout flow:
# creates a complete test user and profile
# opens /
# clicks login
# submits credentials
# confirms redirect to /home
# clicks the Log out navbar link
# confirms redirect back to /index
# confirms the login trigger is visible again
def test_login_and_logout_flow(live_server_url, browser):
    unique_id = uuid4().hex
    email = f"login-{unique_id}@example.com"
    password = "Password123"

    with app.app_context():
        interest = Interest.query.filter_by(name="Sports").first()
        if not interest:
            interest = Interest(name="Sports")
            db.session.add(interest)
            db.session.flush()

        user = User(email=email)
        user.set_password(password)
        profile = Profile(
            user=user,
            display_name="Selenium Tester",
            age=28,
            gender="male",
            orientation="straight",
            location_text="Melbourne VIC",
            latitude=-37.8136,
            longitude=144.9631,
            place_id=f"melbourne-{unique_id}",
            bio="Testing login and logout flows.",
        )
        profile.interests.append(interest)
        db.session.add(user)
        db.session.commit()

    browser.get(live_server_url + "/")

    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "openLogin"))
    ).click()

    email_input = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    password_input = browser.find_element(By.ID, "password")
    submit_button = browser.find_element(By.CSS_SELECTOR, ".login-btn")

    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_button.click()

    WebDriverWait(browser, 5).until(EC.url_contains("/home"))

    assert browser.current_url.endswith("/home")
    assert browser.find_element(By.XPATH, "//h1[contains(text(), 'Welcome back, Selenium Tester')]")

    logout_link = browser.find_element(By.LINK_TEXT, "Log out")
    logout_link.click()

    WebDriverWait(browser, 5).until(EC.url_contains("/index"))
    assert browser.find_element(By.ID, "openLogin").is_displayed()
