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
from app.models import Interest, Likes, Profile, User


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


@pytest.fixture()
def matches_users():
    unique_id = uuid4().hex
    password = "Password123"

    with app.app_context():
        interest = Interest.query.filter_by(name="Sports").first()
        if not interest:
            interest = Interest(name="Sports")
            db.session.add(interest)
            db.session.flush()

        email = f"matches-user-{unique_id}@example.com"
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        profile = Profile(
            user_id=user.id,
            display_name="Match User",
            age=27,
            gender="male",
            orientation="straight",
            location_text="Perth WA",
            latitude=-31.9523,
            longitude=115.8613,
            place_id=f"perth-match-{unique_id}",
            bio="User with match data.",
        )
        profile.interests.append(interest)
        db.session.add(profile)

        contact_email = f"match-contact-{unique_id}@example.com"
        contact_user = User(email=contact_email)
        contact_user.set_password(password)
        db.session.add(contact_user)
        db.session.flush()

        contact_profile = Profile(
            user_id=contact_user.id,
            display_name="Match Contact",
            age=26,
            gender="female",
            orientation="straight",
            location_text="Fremantle WA",
            latitude=-32.0569,
            longitude=115.7439,
            place_id=f"fremantle-match-{unique_id}",
            bio="A contact who likes and is liked.",
        )
        contact_profile.interests.append(interest)
        db.session.add(contact_profile)
        db.session.flush()

        db.session.add_all([
            Likes(liker_id=profile.id, liked_id=contact_profile.id),
            Likes(liker_id=contact_profile.id, liked_id=profile.id),
        ])
        db.session.commit()

    return {
        "email": email,
        "password": password,
        "contact_name": "Match Contact",
    }


def test_matches_page_shows_liked_you_and_you_liked_cards(
    live_server_url,
    browser,
    matches_users,
):
    browser.get(live_server_url + "/")

    login_button = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "openLogin"))
    )
    login_button.click()

    email_input = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    password_input = browser.find_element(By.ID, "password")
    email_input.send_keys(matches_users["email"])
    password_input.send_keys(matches_users["password"])
    browser.find_element(By.CSS_SELECTOR, ".login-btn").click()

    WebDriverWait(browser, 5).until(EC.url_contains("/home"))
    browser.get(live_server_url + "/matches")

    liked_you_card = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//div[@id='likedYouList']//h5[contains(text(), 'Match Contact')]",
            )
        )
    )
    you_liked_card = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located(
            (
                By.XPATH,
                "//div[@id='youLikedList']//h5[contains(text(), 'Match Contact')]",
            )
        )
    )

    assert liked_you_card.is_displayed()
    assert you_liked_card.is_displayed()
    assert browser.find_element(By.CSS_SELECTOR, "h2.fw-bold").text == "People Who Liked You"
