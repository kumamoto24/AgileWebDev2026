from uuid import uuid4

from sqlalchemy import and_, or_

from app import app, db
from app.models import Conversation, Interest, Likes, Profile, User


def create_complete_profile(email, display_name, interest):
    user = User(email=email)
    user.set_password("Password123")
    db.session.add(user)
    db.session.flush()

    profile = Profile(
        user_id=user.id,
        display_name=display_name,
        age=24,
        gender="female",
        orientation="straight",
        location_text="Perth WA",
        latitude=-31.9523,
        longitude=115.8613,
        place_id=f"place-{uuid4().hex}",
        bio="Ready to chat.",
    )
    profile.interests.append(interest)
    db.session.add(profile)

    return user, profile


def test_liking_profile_creates_conversation_once():
    unique_id = uuid4().hex

    with app.app_context():
        interest = Interest.query.filter_by(name="Sports").first()
        if not interest:
            interest = Interest(name="Sports")
            db.session.add(interest)
            db.session.flush()

        current_user, current_profile = create_complete_profile(
            f"like-conversation-user-{unique_id}@example.com",
            "Like Conversation User",
            interest
        )
        _, liked_profile = create_complete_profile(
            f"like-conversation-contact-{unique_id}@example.com",
            "Like Conversation Contact",
            interest
        )
        db.session.commit()

        current_profile_id = current_profile.id
        liked_profile_id = liked_profile.id
        email = current_user.email

    client = app.test_client()
    login_response = client.post(
        "/login",
        data={
            "email": email,
            "password": "Password123",
        },
    )

    assert login_response.status_code == 302

    first_response = client.post(
        f"/profile/{liked_profile_id}/like",
        json={"action": "like"},
    )
    second_response = client.post(
        f"/profile/{liked_profile_id}/like",
        json={"action": "like"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    with app.app_context():
        like = Likes.query.filter_by(
            liker_id=current_profile_id,
            liked_id=liked_profile_id
        ).first()

        profile1_id, profile2_id = sorted([current_profile_id, liked_profile_id])
        conversations = Conversation.query.filter_by(
            profile1_id=profile1_id,
            profile2_id=profile2_id
        ).all()

        assert like is not None
        assert len(conversations) == 1
        assert first_response.get_json()["conversation_id"] == conversations[0].id
        assert second_response.get_json()["conversation_id"] == conversations[0].id


def test_liking_profile_reuses_existing_reverse_conversation():
    unique_id = uuid4().hex

    with app.app_context():
        interest = Interest.query.filter_by(name="Sports").first()
        if not interest:
            interest = Interest(name="Sports")
            db.session.add(interest)
            db.session.flush()

        current_user, current_profile = create_complete_profile(
            f"reverse-conversation-user-{unique_id}@example.com",
            "Reverse Conversation User",
            interest
        )
        _, liked_profile = create_complete_profile(
            f"reverse-conversation-contact-{unique_id}@example.com",
            "Reverse Conversation Contact",
            interest
        )
        db.session.flush()

        existing_conversation = Conversation(
            profile1_id=liked_profile.id,
            profile2_id=current_profile.id
        )
        db.session.add(existing_conversation)
        db.session.commit()

        current_profile_id = current_profile.id
        liked_profile_id = liked_profile.id
        conversation_id = existing_conversation.id
        email = current_user.email

    client = app.test_client()
    login_response = client.post(
        "/login",
        data={
            "email": email,
            "password": "Password123",
        },
    )

    assert login_response.status_code == 302

    response = client.post(
        f"/profile/{liked_profile_id}/like",
        json={"action": "like"},
    )

    assert response.status_code == 200

    with app.app_context():
        conversations = Conversation.query.filter(or_(
            and_(
                Conversation.profile1_id == current_profile_id,
                Conversation.profile2_id == liked_profile_id
            ),
            and_(
                Conversation.profile1_id == liked_profile_id,
                Conversation.profile2_id == current_profile_id
            )
        )).all()

        assert len(conversations) == 1
        assert response.get_json()["conversation_id"] == conversation_id


def test_like_back_reuses_existing_conversation():
    unique_id = uuid4().hex

    with app.app_context():
        interest = Interest.query.filter_by(name="Sports").first()
        if not interest:
            interest = Interest(name="Sports")
            db.session.add(interest)
            db.session.flush()

        user_a, profile_a = create_complete_profile(
            f"like-back-a-{unique_id}@example.com",
            "Like Back User A",
            interest
        )
        user_b, profile_b = create_complete_profile(
            f"like-back-b-{unique_id}@example.com",
            "Like Back User B",
            interest
        )
        db.session.commit()

        profile_a_id = profile_a.id
        profile_b_id = profile_b.id
        email_a = user_a.email
        email_b = user_b.email

    client_a = app.test_client()
    login_a_response = client_a.post(
        "/login",
        data={
            "email": email_a,
            "password": "Password123",
        },
    )
    assert login_a_response.status_code == 302

    a_likes_b_response = client_a.post(
        f"/profile/{profile_b_id}/like",
        json={"action": "like"},
    )
    assert a_likes_b_response.status_code == 200
    conversation_id = a_likes_b_response.get_json()["conversation_id"]

    client_b = app.test_client()
    login_b_response = client_b.post(
        "/login",
        data={
            "email": email_b,
            "password": "Password123",
        },
    )
    assert login_b_response.status_code == 302

    b_likes_a_response = client_b.post(
        f"/profile/{profile_a_id}/like",
        json={"action": "like"},
    )
    assert b_likes_a_response.status_code == 200

    with app.app_context():
        conversations = Conversation.query.filter(or_(
            and_(
                Conversation.profile1_id == profile_a_id,
                Conversation.profile2_id == profile_b_id
            ),
            and_(
                Conversation.profile1_id == profile_b_id,
                Conversation.profile2_id == profile_a_id
            )
        )).all()

        assert len(conversations) == 1
        assert b_likes_a_response.get_json()["conversation_id"] == conversation_id
