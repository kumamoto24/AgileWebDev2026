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
        server = make_server("127.0.0.1", 0, app, threaded=True)
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


@pytest.fixture()
def logged_in_homepage_users():
    unique_id = uuid4().hex
    password = "Password123"

    with app.app_context():
        sports = Interest.query.filter_by(name="Sports").first()
        if not sports:
            sports = Interest(name="Sports")
            db.session.add(sports)

        music = Interest.query.filter_by(name="Music").first()
        if not music:
            music = Interest(name="Music")
            db.session.add(music)

        current_user = User(email=f"home-user-{unique_id}@example.com")
        current_user.set_password(password)
        db.session.add(current_user)
        db.session.flush()

        current_profile = Profile(
            user_id=current_user.id,
            display_name="Test Home User",
            age=22,
            gender="male",
            orientation="straight",
            location_text="Perth WA",
            latitude=-31.9523,
            longitude=115.8613,
            place_id=f"perth-{unique_id}",
            bio="Ready to test the homepage.",
        )
        current_profile.interests.append(sports)
        db.session.add(current_profile)

        recommended_user = User(email=f"recommended-{unique_id}@example.com")
        recommended_user.set_password(password)
        db.session.add(recommended_user)
        db.session.flush()

        recommended_profile = Profile(
            user_id=recommended_user.id,
            display_name="Recommended Tester",
            age=21,
            gender="female",
            orientation="straight",
            location_text="Fremantle WA",
            latitude=-32.0569,
            longitude=115.7439,
            place_id=f"fremantle-{unique_id}",
            bio="A recommended profile for Selenium.",
        )
        recommended_profile.interests.extend([sports, music])
        db.session.add(recommended_profile)
        db.session.commit()

        login_details = {
            "email": current_user.email,
            "password": password,
        }

    yield login_details


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
