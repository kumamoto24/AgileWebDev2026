from app import db
from app.models import Conversation
from sqlalchemy import and_, or_


def ordered_profile_ids(profile_a_id, profile_b_id):
    profile_a_id = int(profile_a_id)
    profile_b_id = int(profile_b_id)

    if profile_a_id < profile_b_id:
        return profile_a_id, profile_b_id

    return profile_b_id, profile_a_id


def get_or_create_conversation(profile_a_id, profile_b_id, commit=True):
    profile1_id, profile2_id = ordered_profile_ids(profile_a_id, profile_b_id)

    conversation = Conversation.query.filter(or_(
        and_(
            Conversation.profile1_id == profile1_id,
            Conversation.profile2_id == profile2_id
        ),
        and_(
            Conversation.profile1_id == profile2_id,
            Conversation.profile2_id == profile1_id
        )
    )).first()

    if conversation:
        return conversation

    conversation = Conversation(
        profile1_id=profile1_id,
        profile2_id=profile2_id
    )

    db.session.add(conversation)

    if commit:
        db.session.commit()
    else:
        db.session.flush()

    return conversation
