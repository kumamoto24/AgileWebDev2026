from flask import Blueprint, abort, jsonify, render_template, request
from flask_login import current_user, login_required

from app import db
from app.conversations import get_or_create_conversation
from app.decorators import profile_required
from app.helpers import profile_to_card
from app.models import Likes, Profile


matches_bp = Blueprint("matches", __name__)


@matches_bp.route("/profile/<int:profile_id>/like", methods=["POST"])
@login_required
@profile_required
def handle_like(profile_id):
    current_profile = current_user.profile
    liked_profile = db.session.get(Profile, profile_id)
    if liked_profile is None:
        abort(404)

    if liked_profile.id == current_profile.id:
        return jsonify({"status": "error", "message": "You cannot like yourself."}), 400

    data = request.get_json(silent=True) or {}
    action = data.get("action")

    existing_like = Likes.query.filter_by(
        liker_id=current_profile.id,
        liked_id=liked_profile.id
    ).first()

    if action == "like":
        if not existing_like:
            db.session.add(Likes(
                liker_id=current_profile.id,
                liked_id=liked_profile.id
            ))

        conversation = get_or_create_conversation(
            current_profile.id,
            liked_profile.id,
            commit=False
        )
        db.session.commit()

        return jsonify({
            "status": "success",
            "is_liked": True,
            "conversation_id": conversation.id
        }), 200

    if action == "unlike":
        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
        return jsonify({"status": "success", "is_liked": False}), 200

    return jsonify({"status": "error", "message": "Invalid like action."}), 400


@matches_bp.route("/matches")
@login_required
@profile_required
def matches():
    return render_template(
        "matches.html",
        is_logged_in=True
    )


@matches_bp.route("/api/matches")
@login_required
@profile_required
def api_matches():
    likes = Likes.query.filter_by(
        liked_id=current_user.profile.id
    ).all()

    liker = []

    for like in likes:
        liker_profile = db.session.get(Profile, like.liker_id)

        if liker_profile:
            liker.append(profile_to_card(liker_profile))

    liked_likes = Likes.query.filter_by(
        liker_id=current_user.profile.id
    ).all()

    liked = []

    for like in liked_likes:
        liked_profile = db.session.get(Profile, like.liked_id)

        if liked_profile:
            liked.append(profile_to_card(liked_profile))

    return jsonify({
        "likerprofiles": liker,
        "likedprofiles": liked
    })
