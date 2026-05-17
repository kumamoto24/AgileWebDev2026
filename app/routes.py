from flask import flash, render_template, jsonify, request, redirect, url_for, current_app, abort
from app import app, db
import os
from sqlalchemy import or_
from app.conversations import get_or_create_conversation
from app.models import Profile, Interest, User, Likes, Story, Conversation
from app.helpers import (
    AGE_RANGES,
    ALL_INTERESTS,
    build_profile_image_url,
    build_story_image_url,
    build_story_slots,
    calculate_distance_km,
    calculate_match_score,
    compatible,
    get_feature_profile,
    is_allowed_age_range,
    profile_to_card,
)
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import requests
from functools import wraps

# Decrorator: constraints for new users who did not complete profile
def profile_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))

        profile = current_user.profile

        if not profile or not profile.is_complete:
            flash("Please complete your profile first.")
            return redirect(url_for("profile"))

        return view_func(*args, **kwargs)

    return wrapped_view


@app.route("/")
@app.route("/index")
def index():
    return render_template(
        "index.html", 
        is_logged_in=False,
        profiles= get_feature_profile())


@app.route("/home")
@login_required
@profile_required
def home():

    current_profile = current_user.profile

    username = (
        current_profile.display_name
        if current_profile
        else "Demo User"
    )

    return render_template(
        "logged_in_homepage.html",
        username=username,
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        interests_list=ALL_INTERESTS,
        age_ranges=AGE_RANGES,
        is_logged_in=True
    )



@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Check required fields
        if not email or not password or not confirm_password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Please complete all required fields.",
                site_key=app.config["RECAPTCHA_SITE_KEY"]
            )
            
        # Password length validation
        if len(password) < 8 or len(password) > 64:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Password must be between 8 and 64 characters.",
                site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        # Check passwords match
        if password != confirm_password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Passwords do not match.",
                site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Email already registered.",
                site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

            # Verify reCAPTCHA
        captcha_response = request.form.get("g-recaptcha-response")

        secret_key = app.config["RECAPTCHA_SECRET_KEY"]

        verify_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": secret_key,
                "response": captcha_response
            }
        )

        result = verify_response.json()

        if not result.get("success"):
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Please complete the CAPTCHA.",
                site_key=app.config["RECAPTCHA_SITE_KEY"]
            )

        # 1. Create and Save the User
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        # Use flush to get the new_user.id before the final commit
        db.session.flush() 

        # 2. AUTOMATIC PROFILE CREATION
        # We create a blank profile so the 'myprofile' page has data to find
        new_profile = Profile(
            id = new_user.id,
            user_id=new_user.id
        )
        db.session.add(new_profile)
        
        # Finalize both User and Profile in the database
        db.session.commit()

        # 3. AUTO-LOGIN
        # Let Flask-Login manage the login session.
        login_user(new_user)

        # 4. REDIRECT TO PROFILE
        # Direct them to fill out their bio and interests
        return redirect(url_for("profile"))

    return render_template(
        "signup.html",
        is_logged_in=False,
        site_key=app.config["RECAPTCHA_SITE_KEY"]
    )


@app.route("/api/recommended-profiles")
@login_required
@profile_required
def recommended_profiles():

    if not current_user.is_authenticated:
        return jsonify([])
    
    current_profile = current_user.profile

    if not current_profile:
        return jsonify([])

    current_interest_names = {
        interest.name for interest in current_profile.interests
    }

    candidate_profiles = (
        Profile.query
        .filter(Profile.id != current_profile.id)
        .all()
    )

    recommendations = []

    for candidate in candidate_profiles:
        if not candidate.is_complete:
            continue

        if not compatible(current_profile, candidate):
            continue

        candidate_interest_names = {
            interest.name for interest in candidate.interests
        }

        shared_interests = current_interest_names.intersection(candidate_interest_names)
        shared_interest_count = len(shared_interests)

        distance = calculate_distance_km(
            current_profile.latitude,
            current_profile.longitude,
            candidate.latitude,
            candidate.longitude
        )

        match_score = calculate_match_score(
            shared_interest_count=shared_interest_count,
            distance=distance,
            candidate=candidate
        )

        recommendations.append(
            profile_to_card(
                candidate,
                distance=distance,
                match_score=match_score
            )
        )

    recommendations.sort(
        key=lambda profile: profile["match_score"],
        reverse=True
    )

    return jsonify(recommendations[:12])


@app.route("/api/search-profiles", methods=["GET"])
@login_required
@profile_required
def search_profiles():
    keyword = request.args.get("keyword", "").strip()

    selected_interests = [
        interest.strip()
        for interest in request.args.getlist("interests")
        if interest.strip()
    ]

    search_latitude = request.args.get("latitude", type=float)
    search_longitude = request.args.get("longitude", type=float)
    radius_km = request.args.get("radius_km", default=10, type=float)
    min_age = request.args.get("min_age", type=int)
    max_age = request.args.get("max_age", type=int)

    if not is_allowed_age_range(min_age, max_age):
        min_age = None
        max_age = None

    current_profile = current_user.profile

    if current_profile is None:
        return jsonify({
            "profiles": []
        })

    query = Profile.query

    # Do not return the current user's own profile.
    query = query.filter(Profile.id != current_profile.id)

    if keyword:
        query = query.filter(
            db.or_(
                Profile.display_name.ilike(f"%{keyword}%"),
                Profile.bio.ilike(f"%{keyword}%"),
                Profile.location_text.ilike(f"%{keyword}%")
            )
        )

    if selected_interests:
        query = (
            query
            .join(Profile.interests)
            .filter(Interest.name.in_(selected_interests))
            .distinct()
        )

    if min_age is not None:
        query = query.filter(Profile.age >= min_age)

    if max_age is not None:
        query = query.filter(Profile.age <= max_age)

    candidate_profiles = query.all()

    results = []

    for profile in candidate_profiles:
        if not profile.is_complete:
            continue
        # Filter the correct orientation
        if not compatible(current_profile, profile):
            continue
        # 1. Search bar location is used only to filter search results.
        if search_latitude is not None and search_longitude is not None:
            distance_from_search_location = calculate_distance_km(
                search_latitude,
                search_longitude,
                profile.latitude,
                profile.longitude
            )
            # Threshold: 10km
            if distance_from_search_location > radius_km:
                continue

        # 2. Profile card distance is calculated from the current user's location.
        distance_from_current_user = calculate_distance_km(
            current_profile.latitude,
            current_profile.longitude,
            profile.latitude,
            profile.longitude
        )

        results.append({
            "id": profile.id,
            "name": profile.display_name,
            "age": profile.age,
            "location": profile.location_text,
            "interests": [interest.name for interest in profile.interests],
            "image": build_profile_image_url(profile.profile_image_path),
            "distance": distance_from_current_user
        })

    return jsonify(results)



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    # 2. SEARCH: Find the user's profile
    user_profile = current_user.profile

    # 3. HANDLE POST (Saving data)
    if request.method == "POST":
        # If no profile exists, create it now to satisfy NOT NULL constraints
        if not user_profile:
            user_profile = Profile(user_id=current_user.id)
            db.session.add(user_profile)

        # Assign values from the form
        user_profile.display_name = request.form.get("display_name")
        user_profile.age = request.form.get("age", type=int)
        user_profile.bio = request.form.get("bio")
        user_profile.gender = request.form.get("gender")
        user_profile.orientation = request.form.get("orientation")
        user_profile.location_text = request.form.get("location_text")
        user_profile.latitude = request.form.get("latitude", type=float)
        user_profile.longitude = request.form.get("longitude", type=float)
        user_profile.place_id = request.form.get("place_id")
        
        # Handle interests
        submitted_interests = request.form.getlist("interest")
        user_profile.interests = [] 
        for name in submitted_interests:
            interest_obj = Interest.query.filter_by(name=name).first()
            if interest_obj:
                user_profile.interests.append(interest_obj)

        db.session.commit()
        # Redirect back to the dynamic URL
        return redirect(url_for("profile"))
    
    # 4. HANDLE GET (Displaying data)
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

@app.route("/profile/<int:profile_id>")
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

@app.route("/profile/<int:profile_id>/like", methods=["POST"])
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


@app.route("/profile/image", methods=["POST"])
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


@app.route("/update-story", methods=["POST"])
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
        story.image_path = f"{upload_subdir}/{filename}" # Fix image upload bug on Windows OS

    db.session.commit()

    return jsonify({
    "status": "success",
    "title": story.title,
    "description": story.description,
    "image_path": story.image_path,
    "image_url": build_story_image_url(story.image_path)
}), 200

@app.route("/matches")
@login_required
@profile_required
def matches():
    return render_template(
        "matches.html",
        is_logged_in=True
    )

@app.route("/api/matches")
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



@app.route("/messages", methods=["GET", "POST"])
@login_required
@profile_required
def messages():
    current_profile = current_user.profile

    contacts = []

    if current_profile:
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


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        #Validating input
        if not email or not password:
            return render_template(
                "index.html",
                is_logged_in=False,
                show_login_modal=True,
                login_error="Please enter both email and password."
            )

        #Find user in DB
        user = User.query.filter_by(email=email).first()

        #Check user exists + password is correct
        if not user or not user.check_password(password):
            return render_template(
                "index.html",
                is_logged_in=False,
                show_login_modal=True,
                login_error="Invalid email or password."
            )
        
        remember = request.form.get("remember") == "on"


        # Create Flask-Login session
        login_user(user, remember=remember)

        #Redirect after login
        return redirect(url_for("home"))

    return render_template(
        "index.html",
        is_logged_in=False,
        profiles=get_feature_profile(),
        show_login_modal=True
    )


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("index"))
