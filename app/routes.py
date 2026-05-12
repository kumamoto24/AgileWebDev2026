from flask import flash, render_template, jsonify, request, redirect, url_for, current_app, session
from app import app
import os
#Database acess
from app import db

from sqlalchemy import or_
from app.models import Profile, Interest, User

from math import radians, sin, cos, sqrt, atan2

#Helper function: Load image
def build_profile_image_url(image_path):
    if not image_path:
        return url_for("static", filename="images/default-profile.png")

    if image_path.startswith(("http://", "https://", "/static/")):
        return image_path

    return url_for("static", filename=image_path)

#Helper function: Convert progiles to cards
def profile_to_card(profile, distance=None, match_score=None):
    return {
        "id": profile.id,
        "name": profile.display_name,
        "age": profile.age,
        "location": profile.location_text,
        "interests": [interest.name for interest in profile.interests],
        "image": build_profile_image_url(profile.profile_image_path),
        "distance": distance,
        "match_score": match_score,
    }

# Helper function: Calculate distance
def calculate_distance_km(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return None

    earth_radius_km = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius_km * c, 1)

#Some sample profile cards to show how the webpage looks like
sample_profiles = [
    {
        "id": 1,
        "name": "Alice",
        "age": 21,
        "location": "Perth",
        "interests": ["Music", "Travel", "Coffee"],
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=300&fit=crop",
        "distance": 2.5,
    },
    {
        "id": 2,
        "name": "Ben",
        "age": 23,
        "location": "Sydney",
        "interests": ["Gaming", "Movies", "Food"],
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=300&fit=crop",
        "distance": 6.8,
    },
    {
        "id": 3,
        "name": "Cathy",
        "age": 22,
        "location": "Melbourne",
        "interests": ["Art", "Photography", "Reading"],
        "image": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=300&fit=crop",
        "distance": 10.2,
    },
]
# Interest list (global)
all_interests = ["Sports","Music","Movies","Travel","Gaming","Reading","Cooking","Fitness","Art","Technology"]

# Helper function: filter compatible recommended candidate
def compatible(current_profile, candidate):
    current_gender = current_profile.gender.lower()
    current_orientation = current_profile.orientation.lower()

    candidate_gender = candidate.gender.lower()
    candidate_orientation = candidate.orientation.lower()

    if current_orientation == "straight":
        if current_gender == "male":
            return candidate_gender == "female" and candidate_orientation == "straight"
        if current_gender == "female":
            return candidate_gender == "male" and candidate_orientation == "straight"
        return True

    # Based on same sexual-orientation
    if current_orientation == "gay":
        return candidate_orientation == "gay"

    if current_orientation == "lesbian":
        return candidate_orientation == "lesbian"

    # For "other", keep the filter open for now
    return True

# Helper function: Calculate match score
def calculate_match_score(shared_interest_count, distance, candidate):
    # The total score would be 100

    # Shared interest score: max 30
    interest_score = min(shared_interest_count * 10, 30)

    # Calculate the distance score: max 60
    if distance is None:
        distance_score = 0
    elif distance <= 5:
        distance_score = 60
    elif distance <= 10:
        distance_score = 55
    elif distance <= 20:
        distance_score = 50
    elif distance <= 50:
        distance_score = 35
    elif distance <= 100:
        distance_score = 20
    elif distance <= 500:
        distance_score = 5
    else:
        distance_score = 0

    # The profile completeness score: max 10
    completeness_score = 0

    if candidate.bio:
        completeness_score += 3

    if candidate.profile_image_path:
        completeness_score += 3

    if candidate.interests:
        completeness_score += 4

    return interest_score + distance_score + completeness_score

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", is_logged_in=False,profiles=sample_profiles)


@app.route("/home")
def home():

    '''
    # Temporary: use the first profile as the current user profile
    current_profile = Profile.query.first()
    '''
    # Give back the login session
    if "user_id" not in session:
        return redirect(url_for("index"))

    current_user = User.query.get(session["user_id"])
    current_profile = current_user.profile if current_user else None

    username = (
        current_profile.display_name
        if current_profile
        else "Demo User"
    )

    return render_template(
        "logged_in_homepage.html",
        username=username,
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
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
                signup_error="Please complete all required fields."
            )
            
        # Password length validation
        if len(password) < 8 or len(password) > 64:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Password must be between 8 and 64 characters."
            )

        # Check passwords match
        if password != confirm_password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Passwords do not match."
            )

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Email already registered."
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
            user_id=new_user.id,
            display_name="", # Placeholder name
            age="",                   # Required field default
            gender="",    # For recommendation algorithm
            orientation="",
            location_text="",
            latitude="",
            longitude="",
            place_id="default"
        )
        db.session.add(new_profile)
        
        # Finalize both User and Profile in the database
        db.session.commit()

        # 3. AUTO-LOGIN
        # Store the ID in session so they are 'logged in' immediately
        session["user_id"] = new_user.id

        # 4. REDIRECT TO PROFILE
        # Direct them to fill out their bio and interests
        return redirect(url_for("profile"))

    return render_template(
        "signup.html",
        is_logged_in=False
    )


@app.route("/api/recommended-profiles")
def recommended_profiles():
    '''
    # Temporary: use the first profile as the current user profile (login has not been developed)
    current_profile = Profile.query.first()
    '''

    if "user_id" not in session:
        return redirect(url_for("index"))

    current_user = User.query.get(session["user_id"])
    current_profile = current_user.profile if current_user else None

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

    if "user_id" not in session:
        return redirect(url_for("index"))

    current_user = User.query.get(session["user_id"])
    current_profile = current_user.profile if current_user else None
    
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

    candidate_profiles = query.all()

    results = []

    for profile in candidate_profiles:
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
def profile():
    # Ensure user is logged in
    if "user_id" not in session:
        return redirect(url_for("signup"))
    
    user_id = session['user_id']
    user_profile = Profile.query.filter_by(user_id=user_id).first()

    # HANDLE SAVING DATA (POST)
    if request.method == "POST":
        if not user_profile:
            user_profile = Profile(user_id=user_id)
            db.session.add(user_profile)

        # Update fields
        user_profile.display_name = request.form.get("name")
        user_profile.bio = request.form.get("bio")
        user_profile.gender = request.form.get("gender")
        user_profile.orientation = request.form.get("orientation")
        
        # Handle interests
        submitted_interests = request.form.getlist("interest")
        user_profile.interests = [] 
        for name in submitted_interests:
            interest_obj = Interest.query.filter_by(name=name).first()
            if interest_obj:
                user_profile.interests.append(interest_obj)

        db.session.commit()
        # Stay on the same page after saving
        return redirect(url_for('profile'))
    
    # HANDLE DISPLAYING DATA (GET)
    all_interests = Interest.query.all()
    return render_template(
        "myprofile.html",
        interests_list=all_interests,
        user=user_profile, 
        is_logged_in=True
    )


@app.route("/profile/<int:profile_id>")
def profile_detail(user_id):
    # If the user is looking at their own ID, send them to the edit page instead
    if "user_id" in session and session['user_id'] == user_id:
        return redirect(url_for("profile"))

    target_profile = Profile.query.filter_by(user_id=user_id).first_or_404()
    return render_template(
        "userprofile.html",
        profile=target_profile,
        is_logged_in="user_id" in session
    )


@app.route("/profile/<int:profile_id>/like", methods=["POST"])
def handle_like(profile_id):
    # This logic only runs when the 'Like' button is clicked, 
    # it does not load a new page.
    data = request.get_json()
    print(f"Received {data.get('action')} for profile {profile_id}")
    return jsonify({"status": "success"}), 200


# @app.route("/profile/update", methods=["POST"])
# def update_profile():
#     User.name = request.form.get("name")
#     db.session.commit()
#     return redirect(url_for('profile'))


@app.route("/story/update", methods=["POST"])
def update_story():
    title = request.form.get("title")
    description = request.form.get("description")
    image_file = request.files.get("story_image")
    
    # Validation and save logic...
    return jsonify({"status": "success"}), 200

# '/matches' to be deleted
@app.route("/matches")
def matches():

    if "user_id" not in session:
        return redirect(url_for("index"))

    return "Matches page placeholder"


@app.route("/messages", methods=["GET", "POST"])
def messages():

    if "user_id" not in session:
        return redirect(url_for("index"))

    current_user = User.query.get(session["user_id"])
    current_profile = current_user.profile if current_user else None

    contacts = []

    if current_profile:
        candidate_profiles = (
            Profile.query
            .filter(Profile.id != current_profile.id)
            .order_by(Profile.display_name)
            .all()
        )

        contacts = [
            profile_to_card(profile)
            for profile in candidate_profiles
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

        #Create session
        session["user_id"] = user.id
        session["email"] = user.email

        #Redirect after login
        return redirect(url_for("home"))

    return render_template(
        "index.html",
        is_logged_in=False,
        profiles=sample_profiles,
        show_login_modal=True
    )


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))
