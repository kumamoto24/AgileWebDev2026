from flask import session
from flask_socketio import join_room, emit, disconnect

from app import socketio, db
from app.models import Profile, Conversation, Message, User


def ordered_profile_ids(profile_a_id, profile_b_id):
    profile_a_id = int(profile_a_id)
    profile_b_id = int(profile_b_id)

    if profile_a_id < profile_b_id:
        return profile_a_id, profile_b_id

    return profile_b_id, profile_a_id


def get_or_create_conversation(profile_a_id, profile_b_id):
    profile1_id, profile2_id = ordered_profile_ids(profile_a_id, profile_b_id)

    conversation = Conversation.query.filter_by(
        profile1_id=profile1_id,
        profile2_id=profile2_id
    ).first()

    if conversation:
        return conversation

    conversation = Conversation(
        profile1_id=profile1_id,
        profile2_id=profile2_id
    )

    db.session.add(conversation)
    db.session.commit()

    return conversation


def get_current_profile():
    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(User, user_id)

    if not user:
        return None

    return user.profile


def profile_room(profile_id):
    return f"profile_{profile_id}"


def serialize_message(message):
    sender = db.session.get(Profile, message.sender_profile_id)

    return {
        "id": message.id,
        "recipientId": message.receiver_profile_id,
        "senderId": message.sender_profile_id,
        "senderName": sender.display_name if sender else "Unknown",
        "body": message.body,
        "createdAt": message.created_at.isoformat()
    }


@socketio.on("connect")
def handle_connect(auth=None):
    current_profile = get_current_profile()

    if not current_profile:
        return False

    join_room(profile_room(current_profile.id))


@socketio.on("chat:join")
def handle_chat_join(data):
    current_profile = get_current_profile()

    if not current_profile:
        disconnect()
        return

    recipient_id = data.get("recipientId")

    if not recipient_id:
        return

    recipient = db.session.get(Profile, recipient_id)

    if not recipient:
        return

    if recipient.id == current_profile.id:
        return

    conversation = get_or_create_conversation(
        current_profile.id,
        recipient.id
    )

    messages = (
        Message.query
        .filter_by(conversation_id=conversation.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    emit("chat:history", {
        "contactId": recipient.id,
        "messages": [serialize_message(message) for message in messages]
    })


@socketio.on("chat:send_message")
def handle_send_message(data):
    current_profile = get_current_profile()

    if not current_profile:
        disconnect()
        return

    recipient_id = data.get("recipientId")
    body = (data.get("body") or "").strip()

    if not recipient_id or not body:
        return

    if len(body) > 1000:
        body = body[:1000]

    recipient = db.session.get(Profile, recipient_id)

    if not recipient:
        return

    if recipient.id == current_profile.id:
        return

    conversation = get_or_create_conversation(
        current_profile.id,
        recipient.id
    )

    message = Message(
        conversation_id=conversation.id,
        sender_profile_id=current_profile.id,
        receiver_profile_id=recipient.id,
        body=body
    )

    db.session.add(message)
    db.session.commit()

    emit(
        "chat:new_message",
        serialize_message(message),
        to=profile_room(recipient.id)
    )