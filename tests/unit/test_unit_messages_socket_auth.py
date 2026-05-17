from uuid import uuid4

from app import app, db, socketio
from app.models import Profile, User


def test_logged_in_user_can_connect_to_messages_socket():
    password = "Password123"
    email = f"socket-user-{uuid4().hex}@example.com"

    with app.app_context():
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        db.session.add(
            Profile(
                user_id=user.id,
                display_name="Socket User",
                age=22,
                gender="male",
                orientation="straight",
                location_text="Perth WA",
                latitude=-31.9523,
                longitude=115.8613,
                place_id=f"socket-user-{uuid4().hex}",
            )
        )
        db.session.commit()

    flask_client = app.test_client()
    response = flask_client.post(
        "/login",
        data={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 302

    socket_client = socketio.test_client(
        app,
        flask_test_client=flask_client,
    )

    assert socket_client.is_connected()
