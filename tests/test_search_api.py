import pytest

from app import app, db
from app.models import User, Profile, Interest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()

        music = Interest(name="Music", category="Creative")
        travel = Interest(name="Travel", category="Lifestyle")
        gaming = Interest(name="Gaming", category="Social")

        user1 = User(email="alice@example.com")
        user1.set_password("password")

        user2 = User(email="ben@example.com")
        user2.set_password("password")

        user3 = User(email="cathy@example.com")
        user3.set_password("password")

        profile1 = Profile(
            user=user1,
            display_name="Alice",
            bio="I like music and coffee.",
            age=21,
            gender="Female",
            location_text="Perth",
            latitude=-31.9505,
            longitude=115.8605,
            place_id="perth_place_id",
            profile_image_path="uploads/alice.jpg",
            interests=[music, travel],
        )

        profile2 = Profile(
            user=user2,
            display_name="Ben",
            bio="I enjoy gaming and movies.",
            age=23,
            gender="Male",
            location_text="Sydney",
            latitude=-33.8688,
            longitude=151.2093,
            place_id="sydney_place_id",
            profile_image_path="uploads/ben.jpg",
            interests=[gaming],
        )

        profile3 = Profile(
            user=user3,
            display_name="Cathy",
            bio="Travel and photography are my hobbies.",
            age=22,
            gender="Female",
            location_text="Fremantle",
            latitude=-32.0569,
            longitude=115.7439,
            place_id="fremantle_place_id",
            profile_image_path="uploads/cathy.jpg",
            interests=[travel],
        )

        db.session.add_all([
            music, travel, gaming,
            user1, user2, user3,
            profile1, profile2, profile3,
        ])
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_recommended_profiles_returns_profiles(client):
    response = client.get("/api/recommended-profiles")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_profile = data[0]

    assert "id" in first_profile
    assert "name" in first_profile
    assert "age" in first_profile
    assert "location" in first_profile
    assert "interests" in first_profile
    assert "image" in first_profile

def test_search_profiles_by_keyword(client):
    response = client.get(
        "/api/search-profiles",
        query_string={"keyword": "music"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) >= 1

    names = [profile["name"] for profile in data]

    assert "Alice" in names


def test_search_profiles_by_interest(client):
    response = client.get(
        "/api/search-profiles",
        query_string=[("interests", "Travel")]
    )

    assert response.status_code == 200

    data = response.get_json()

    names = [profile["name"] for profile in data]

    assert "Alice" in names
    assert "Cathy" in names
    assert "Ben" not in names

def test_search_profiles_sorts_by_distance(client):
    response = client.get(
        "/api/search-profiles",
        query_string={
            "latitude": -31.9505,
            "longitude": 115.8605,
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) >= 2

    names = [profile["name"] for profile in data]

    assert names[0] == "Alice"