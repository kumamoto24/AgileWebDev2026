import os
import sys
import threading
from pathlib import Path
from uuid import uuid4

import pytest
from werkzeug.serving import make_server

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_PATH = PROJECT_ROOT / "tests" / "test_app.db"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DATABASE_PATH}")

from app import app, db
from app.models import Interest, Profile, User


def pytest_sessionstart(session):
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        db.create_all()


@pytest.fixture(scope="module")
def live_server_url():
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
    selenium = pytest.importorskip("selenium")

    from selenium import webdriver
    from selenium.common.exceptions import WebDriverException
    from selenium.webdriver.chrome.options import Options

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


def pytest_sessionfinish(session, exitstatus):
    from app import app, db

    with app.app_context():
        db.session.remove()
        db.engine.dispose()

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()
