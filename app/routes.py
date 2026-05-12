from flask import flash, render_template, jsonify, request, redirect, url_for, current_app

from app import app, db
import os


from sqlalchemy import or_
from app.models import Profile, Interest, User

from math import radians, sin, cos, sqrt, atan2

from flask_login import login_user, login_required, current_user, logout_user
from functools import wraps

#Helper function: Load image
def build_profile_image_url(image_path):
    if not image_path:
        return url_for("static", filename="images/default-profile.png")

    if image_path.startswith(("http://", "https://")):
        return image_path
    
    # Handle situation where file does not exist in filesystem
    static_prefix = "/static/"
    if image_path.startswith(static_prefix):
        filename = image_path[len(static_prefix):]  
    else:
        filename = image_path

    full_path = os.path.join(current_app.static_folder, filename)

    if not os.path.exists(full_path):
        return url_for("static", filename="images/default-profile.png")

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


# Helper function: profile required
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
 
# Helper function: get feature profiles
def get_feature_profile():
    featured_profiles = (
        Profile.query
        .order_by(db.func.random())
        .limit(3)
        .all())
    return [profile_to_card(profile) for profile in featured_profiles]


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
        is_logged_in=False
    )


@app.route("/api/recommended-profiles")
@login_required
@profile_required
def recommended_profiles():
    '''
    # Temporary: use the first profile as the current user profile (login has not been developed)
    current_profile = Profile.query.first()
    '''


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

    candidate_profiles = query.all()

    results = []

    for profile in candidate_profiles:
        if not profile.is_complete:
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
    
    return render_template(
        "myprofile.html",
        interests_list=all_interests,
        user=user_profile, 
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        is_logged_in=True
    )

@app.route("/profile/<int:profile_id>")
def profile_detail(profile_id):
    return render_template(
        "userprofile.html",
        profile_id=profile_id
    )

@app.route("/profile/<int:profile_id>/like", methods=["POST"])
def handle_like(profile_id):
    # This logic only runs when the 'Like' button is clicked, 
    # it does not load a new page.
    data = request.get_json()
    print(f"Received {data.get('action')} for profile {profile_id}")
    return jsonify({"status": "success"}), 200


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)

    profile.display_name = request.form.get("display_name")
    profile.age = request.form.get("age", type=int)
    profile.gender = request.form.get("gender")
    profile.orientation = request.form.get("orientation")
    profile.location_text = request.form.get("location_text")
    profile.latitude = request.form.get("latitude", type=float)
    profile.longitude = request.form.get("longitude", type=float)
    profile.place_id = request.form.get("place_id")
    profile.bio = request.form.get("bio")

    submitted_interests = request.form.getlist("interest")
    profile.interests = []
    for name in submitted_interests:
        interest_obj = Interest.query.filter_by(name=name).first()
        if interest_obj:
            profile.interests.append(interest_obj)

    db.session.commit()
    return redirect(url_for("profile"))


@app.route("/story/update", methods=["POST"])
def update_story():
    title = request.form.get("title")
    description = request.form.get("description")
    image_file = request.files.get("story_image")
    
    # Validation and save logic...
    return jsonify({"status": "success"}), 200

# '/matches' to be deleted
@app.route("/matches")
@login_required
@profile_required
def matches():
    return "Matches page placeholder"


@app.route("/messages", methods=["GET", "POST"])
@login_required
@profile_required
def messages():
    current_profile = current_user.profile

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
