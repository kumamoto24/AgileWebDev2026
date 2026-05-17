import pytest
from app import app, db
from app.models import User

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_signup_password_mismatch(client):
    response = client.post("/signup", data={
        "email": "test2@example.com",
        "password": "password123",
        "confirm_password": "wrongpass",
        "g-recaptcha-response": "test"
    })

    assert b"Passwords do not match" in response.data



