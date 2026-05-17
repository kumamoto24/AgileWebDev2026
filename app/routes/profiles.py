import os

from flask import Blueprint, abort, current_app, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app import db
from app.decorators import profile_required
from app.helpers import (
    build_profile_image_url,
    build_story_image_url,
    build_story_slots,
)
from app.models import Interest, Likes, Profile, Story


profiles_bp = Blueprint("profiles", __name__)


@profiles_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_profile = current_user.profile

    if request.method == "POST":
        if not user_profile:
            user_profile = Profile(user_id=current_user.id)
            db.session.add(user_profile)

        user_profile.display_name = request.form.get("display_name")
        user_profile.age = request.form.get("age", type=int)
        user_profile.bio = request.form.get("bio")
        user_profile.gender = request.form.get("gender")
        user_profile.orientation = request.form.get("orientation")
        user_profile.location_text = request.form.get("location_text")
        user_profile.latitude = request.form.get("latitude", type=float)
        user_profile.longitude = request.form.get("longitude", type=float)
        user_profile.place_id = request.form.get("place_id")

        submitted_interests = request.form.getlist("interest")
        user_profile.interests = []
        for name in submitted_interests:
            interest_obj = Interest.query.filter_by(name=name).first()
            if interest_obj:
                user_profile.interests.append(interest_obj)

        db.session.commit()
        return redirect(url_for("profiles.profile"))

    all_interests = Interest.query.all()
    story_slots = build_story_slots(user_profile.stories if user_profile else [])

    return render_template(
        "myprofile.html",
        interests_list=all_interests,
        user=user_profile,
        story_slots=story_slots,
        profile_image_url=build_profile_image_url(user_profile.profile_image_path if user_profile else None),
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        is_logged_in=True
    )


@profiles_bp.route("/profile/<int:profile_id>")
@login_required
@profile_required
def profile_detail(profile_id):
    profile = db.session.get(Profile, profile_id)
    if profile is None:
        abort(404)
    current_profile = current_user.profile

    is_liked = Likes.query.filter_by(
        liker_id=current_profile.id,
        liked_id=profile.id
    ).first() is not None

    stories = [
        {
            "id": story.id,
            "title": story.title,
            "description": story.description,
            "image_url": build_story_image_url(story.image_path),
            "display_order": story.display_order,
        }
        for story in profile.stories
    ]

    profile_data = {
        "id": profile.id,
        "display_name": profile.display_name,
        "age": profile.age,
        "location_text": profile.location_text,
        "gender": profile.gender,
        "orientation": profile.orientation,
        "bio": profile.bio,
        "profile_image_url": build_profile_image_url(profile.profile_image_path),
        "interests": [interest.name for interest in profile.interests],
        "stories": stories,
        "is_liked": is_liked,
    }

    return render_template(
        "userprofile.html",
        profile=profile_data,
        is_logged_in=True
    )


@profiles_bp.route("/profile/image", methods=["POST"])
@login_required
def update_profile_image():
    profile = current_user.profile

    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.flush()

    image_file = request.files.get("profilePicture")

    if not image_file or not image_file.filename:
        return jsonify({
            "status": "error",
            "message": "No profile image was uploaded."
        }), 400

    filename = secure_filename(image_file.filename)
    upload_subdir = "uploads/profile_images"
    upload_folder = os.path.join(current_app.static_folder, upload_subdir)
    os.makedirs(upload_folder, exist_ok=True)

    image_file.save(os.path.join(upload_folder, filename))
    profile.profile_image_path = f"{upload_subdir}/{filename}"

    db.session.commit()

    return jsonify({
        "status": "success",
        "profile_image_path": profile.profile_image_path,
        "profile_image_url": build_profile_image_url(profile.profile_image_path)
    }), 200


@profiles_bp.route("/update-story", methods=["POST"])
@login_required
def update_story():
    profile = current_user.profile

    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)
        db.session.flush()

    display_order = request.form.get("display_order", type=int)

    if display_order not in [1, 2, 3]:
        return jsonify({
            "status": "error",
            "message": "Invalid story slot."
        }), 400

    story = Story.query.filter_by(
        profile_id=profile.id,
        display_order=display_order
    ).first()

    if not story:
        story = Story(
            profile_id=profile.id,
            display_order=display_order,
            image_path="images/default-story.jpg"
        )
        db.session.add(story)

    story.title = request.form.get("title") or "Untitled Story"
    story.description = request.form.get("description")

    image_file = request.files.get("image_path")

    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        upload_subdir = "uploads/story_images"
        upload_folder = current_app.config.get(
            "UPLOAD_FOLDER",
            os.path.join(current_app.static_folder, upload_subdir)
        )
        os.makedirs(upload_folder, exist_ok=True)

        image_file.save(os.path.join(upload_folder, filename))
        story.image_path = f"{upload_subdir}/{filename}"

    db.session.commit()

    return jsonify({
        "status": "success",
        "title": story.title,
        "description": story.description,
        "image_path": story.image_path,
        "image_url": build_story_image_url(story.image_path)
    }), 200
