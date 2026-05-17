from uuid import uuid4

import pytest

selenium = pytest.importorskip("selenium")

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app import app, db
from app.models import Conversation, Interest, Profile, User


def test_messages_page_shows_conversation_and_enables_chat(
    live_server_url,
    browser,
    logged_in_homepage_users,
):
    contact_email = f"message-contact-{uuid4().hex}@example.com"
    contact_password = "Password123"

    with app.app_context():
        contact_user = User(email=contact_email)
        contact_user.set_password(contact_password)
        db.session.add(contact_user)
        db.session.flush()

        contact_profile = Profile(
            user_id=contact_user.id,
            display_name="Message Contact",
            age=26,
            gender="female",
            orientation="straight",
            location_text="Fremantle WA",
            latitude=-32.0569,
            longitude=115.7439,
            place_id=f"fremantle-message-{uuid4().hex}",
            bio="Conversation contact for Selenium.",
        )
        interest = Interest.query.filter_by(name="Sports").first()
        if interest:
            contact_profile.interests.append(interest)

        db.session.add(contact_profile)
        db.session.flush()

        current_user = User.query.filter_by(
            email=logged_in_homepage_users["email"]
        ).first()

        conversation = Conversation(
            profile1_id=current_user.profile.id,
            profile2_id=contact_profile.id,
        )
        db.session.add(conversation)
        db.session.commit()

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

    browser.get(live_server_url + "/messages")

    conversation_button = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".conversation-item"))
    )
    assert "Message Contact" in conversation_button.text
    conversation_button.click()

    WebDriverWait(browser, 5).until(
        EC.text_to_be_present_in_element((By.ID, "activeContactName"), "Message Contact")
    )
    message_input = browser.find_element(By.ID, "messageInput")
    send_button = browser.find_element(By.ID, "sendMessageButton")

    assert message_input.is_enabled()
    assert send_button.is_enabled()
