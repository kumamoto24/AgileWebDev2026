import pytest

selenium = pytest.importorskip("selenium")

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import app, db
from app.models import Profile, Likes


def test_like_creates_db_entry(live_server_url, browser, logged_in_homepage_users):
    # Find the profile ids created by the fixture
    with app.app_context():
        current_profile = Profile.query.filter_by(display_name="Test Home User").first()
        assert current_profile is not None
        target_profile = Profile.query.filter_by(display_name="Recommended Tester").first()
        assert target_profile is not None

    # Open main page and login
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

    # Navigate to the target profile's page
    browser.get(live_server_url + f"/profile/{target_profile.id}")

    like_btn = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "likeBtn"))
    )

    # Ensure initial state is not liked
    assert "Liked" not in like_btn.text

    # Click like and wait for UI to update
    like_btn.click()

    WebDriverWait(browser, 5).until(
        lambda drv: "Liked" in drv.find_element(By.ID, "likeBtn").text
    )

    # Verify DB entry
    with app.app_context():
        like_entry = Likes.query.filter_by(
            liker_id=current_profile.id,
            liked_id=target_profile.id
        ).first()

        assert like_entry is not None

        # Clean up the like so tests are idempotent
        db.session.delete(like_entry)
        db.session.commit()
