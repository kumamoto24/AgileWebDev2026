#NB: This test average time is around 20 seconds due to 2 test cases and the need to create users, conversations and load the homepage for each test.

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
from app.models import Conversation, Interest, Profile, User



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



# Function validates that:

# A conversation exists in the database
# The logged-in user can see it on /messages
# Clicking the conversation opens the chat
# The chat input and send button are enabled
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

        #saving contact profile before creating conversation to ensure it has an ID
        db.session.add(contact_profile)
        db.session.flush()

        current_user = User.query.filter_by(email=logged_in_homepage_users["email"]).first()
        profile_id = current_user.profile.id

        #create conversation     
        conversation = Conversation(
            profile1_id=profile_id,
            profile2_id=contact_profile.id,
        )
        db.session.add(conversation)
        db.session.commit()

    #opening browser
    browser.get(live_server_url + "/")

    #clicks login 
    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "openLogin"))
    ).click()

    email_input = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    email_input.send_keys(logged_in_homepage_users["email"])
    browser.find_element(By.ID, "password").send_keys(logged_in_homepage_users["password"])
    browser.find_element(By.CSS_SELECTOR, ".login-btn").click()

    #confirm webredirect
    WebDriverWait(browser, 5).until(EC.url_contains("/home"))
    #going to messages page
    browser.get(live_server_url + "/messages")

    #Verify conversation is visible
    conversation_button = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".conversation-item"))
    )
    assert "Message Contact" in conversation_button.text
    #The line above Ensures correct user name is shown
    conversation_button.click()


    #Wait for active chat header and onfirms the correct conversation is loaded
    active_contact_name = WebDriverWait(browser, 5).until(
        EC.text_to_be_present_in_element((By.ID, "activeContactName"), "Message Contact")
    )
    message_input = browser.find_element(By.ID, "messageInput")
    send_button = browser.find_element(By.ID, "sendMessageButton")

    #User can type message and send button is enabled
    assert message_input.is_enabled()
    assert send_button.is_enabled()
