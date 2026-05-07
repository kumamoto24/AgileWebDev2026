from flask import render_template, jsonify, request, redirect, url_for, current_app
from app import app
import os

from sqlalchemy import or_
from app.models import Profile, Interest

from math import radians, sin, cos, sqrt, atan2

def build_profile_image_url(image_path):
    if not image_path:
        return url_for("static", filename="images/default-profile.png")

    if image_path.startswith(("http://", "https://", "/static/")):
        return image_path

    return url_for("static", filename=image_path)


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


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", is_logged_in=False,profiles=sample_profiles)


@app.route("/home")
def home():
    return render_template(
        "logged_in_homepage.html",
        username="Demo User",
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        is_logged_in=True
    )

@app.route("/logout", methods=["GET", "POST"])
def logout():
    return "Logout placeholder"

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Please complete all required fields."
            )

        # Placeholder flow until database/user authentication is implemented.
        return redirect(url_for("home"))

    return render_template("signup.html", is_logged_in=False)

@app.route("/api/recommended-profiles")
def recommended_profiles():
    profiles = Profile.query.order_by(Profile.created_at.desc()).limit(12).all()

    return jsonify([
        profile_to_card(profile)
        for profile in profiles
    ])


@app.route("/api/search-profiles", methods=["GET", "POST"])
def search_profiles():
    keyword = request.args.get("keyword", "").strip()

    selected_interests = [
        interest.strip()
        for interest in request.args.getlist("interests")
        if interest.strip()
    ]

    search_latitude = request.args.get("latitude", type=float)
    search_longitude = request.args.get("longitude", type=float)

    query = Profile.query

    # Search by keyword: display name, bio, or interest name
    if keyword:
        keyword_pattern = f"%{keyword}%"

        query = query.filter(
            or_(
                Profile.display_name.ilike(keyword_pattern),
                Profile.bio.ilike(keyword_pattern),
                Profile.interests.any(Interest.name.ilike(keyword_pattern))
            )
        )

    # Search by selected interests
    if selected_interests:
        query = query.filter(
            Profile.interests.any(Interest.name.in_(selected_interests))
        )

    profiles = query.distinct().limit(50).all()

    results = []

    for profile in profiles:
        distance = calculate_distance_km(
            search_latitude,
            search_longitude,
            profile.latitude,
            profile.longitude
        )

        results.append(
            profile_to_card(profile, distance=distance)
        )

    # If the user selected a location, sort results by distance
    if search_latitude is not None and search_longitude is not None:
        results.sort(
            key=lambda profile: (
                profile["distance"]
                if profile["distance"] is not None
                else float("inf")
            )
        )

    return jsonify(results[:30])


@app.route("/profile", methods=["GET", "POST"])
def profile():
    return render_template(
        "myprofile.html",
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        is_logged_in=True
    )


@app.route("/profile/<int:profile_id>")
def profile_detail(profile_id):
    return render_template(
        "userprofile.html",
        profile_id=profile_id
    )

# '/matches' to be deleted
@app.route("/matches")
def matches():
    return "Matches page placeholder"


@app.route("/messages", methods=["GET", "POST"])
def messages():
    return "Messages page placeholder"


@app.route("/login", methods=["GET", "POST"])
def login():
    """Use the login form/modal inside index.html instead of a separate login page."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Temporary demo login logic.
        # Replace this with real database authentication later.
        if email and password:
            return redirect(url_for("home"))

        return render_template(
            "index.html",
            is_logged_in=False,
            profiles=sample_profiles,
            show_login_modal=True,
            login_error="Please enter both email and password."
        )

    return render_template(
        "index.html",
        is_logged_in=False,
        profiles=sample_profiles,
        show_login_modal=True
    )
