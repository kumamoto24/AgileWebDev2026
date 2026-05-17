import pytest

selenium = pytest.importorskip("selenium")

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import os
import tempfile

from app import app
from app.models import Story, User


def test_update_story_creates_and_updates_story(
    live_server_url,
    browser,
    logged_in_homepage_users,
):
    import os
    import base64
    import pytest

    selenium = pytest.importorskip("selenium")

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    from app import app
    from app.models import Story, User


    def test_update_story_creates_and_updates_story(
        live_server_url,
        browser,
        logged_in_homepage_users,
    ):
        # Login via the app's login page
        browser.get(live_server_url + "/login")

        WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "email"))
        ).send_keys(logged_in_homepage_users["email"])

        browser.find_element(By.ID, "password").send_keys(
            logged_in_homepage_users["password"]
        )
        browser.find_element(By.CSS_SELECTOR, ".login-btn").click()

        WebDriverWait(browser, 10).until(EC.url_contains("/home"))

        # Navigate to profile where the story cards live
        browser.get(live_server_url + "/profile")

        story_card = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".story-card[data-story-order='1']"))
        )
        story_card.click()

        WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "storyTitleInput"))
        )

        # Create a tiny PNG image for upload
        png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
        )
        fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
        os.makedirs(fixtures_dir, exist_ok=True)
        img_path = os.path.join(fixtures_dir, "selenium_test.png")
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(png_b64))

        # Clone the form to remove the frontend fetch event listener so we can perform a traditional form POST
        browser.execute_script(
            "const f=document.getElementById('storyForm'); const clone=f.cloneNode(true); f.parentNode.replaceChild(clone,f);"
        )

        # Re-query inputs from the cloned form
        title_input = browser.find_element(By.ID, "storyTitleInput")
        description_input = browser.find_element(By.ID, "storyDescriptionInput")
        file_input = browser.find_element(By.ID, "storyPicInput")

        title_input.clear()
        title_input.send_keys("Selenium Story Title")

        description_input.clear()
        description_input.send_keys("This story was updated by Selenium.")

        # Attach file via input (send_keys requires an existing file path)
        file_input.send_keys(img_path)

        # Ensure display order 1
        browser.execute_script("document.getElementById('storyOrderInput').value = '1';")

        # Submit the cloned form (this will perform a normal multipart POST)
        browser.execute_script("document.getElementById('storyForm').submit();")

        # Allow the server a moment to process — the response is JSON, so the URL will change
        WebDriverWait(browser, 5).until(lambda drv: drv.current_url != live_server_url + "/profile")

        # Verify the story saved on the server
        with app.app_context():
            user = User.query.filter_by(email=logged_in_homepage_users["email"]).first()
            story = Story.query.filter_by(profile_id=user.profile.id, display_order=1).first()

            assert story is not None
            assert story.title == "Selenium Story Title"
            assert story.description == "This story was updated by Selenium."
            assert story.image_path is not None
