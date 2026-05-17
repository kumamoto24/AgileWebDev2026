from flask import Blueprint, render_template
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.decorators import profile_required
from app.helpers import profile_to_card
from app.models import Conversation, Profile


# Routes for displaying the current user's conversation contacts.
messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/messages", methods=["GET", "POST"])
@login_required
@profile_required
def messages():
    # Render conversations as contact cards for the current profile.
    current_profile = current_user.profile

    contacts = []

    if current_profile:
        # Conversations include two profile IDs, so either side can be the current user.
        conversations = (
            Conversation.query
            .filter(or_(
                Conversation.profile1_id == current_profile.id,
                Conversation.profile2_id == current_profile.id
            ))
            .order_by(Conversation.created_at.desc())
            .all()
        )

        contact_ids = [
            conversation.profile2_id
            if conversation.profile1_id == current_profile.id
            else conversation.profile1_id
            for conversation in conversations
        ]

        # Load all contact profiles in one query and keep the conversation order.
        profiles_by_id = {
            profile.id: profile
            for profile in Profile.query.filter(Profile.id.in_(contact_ids)).all()
        } if contact_ids else {}

        contacts = [
            profile_to_card(profiles_by_id[contact_id])
            for contact_id in contact_ids
            if contact_id in profiles_by_id
        ]

    return render_template(
        "messages.html",
        current_profile=current_profile,
        contacts=contacts,
        is_logged_in=True
    )
