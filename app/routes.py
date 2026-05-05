from flask import render_template, jsonify, request, redirect, url_for, current_app
from app import app
import os

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
    return jsonify(sample_profiles)


@app.route("/api/search-profiles", methods=["GET", "POST"])
def search_profiles():
    keyword = request.args.get("keyword", "").lower()
    location = request.args.get("location", "").lower()
    selected_interests = request.args.getlist("interests")

    results = sample_profiles

    if keyword:
        results = [
            profile for profile in results
            if keyword in profile["name"].lower()
            or any(keyword in interest.lower() for interest in profile["interests"])
        ]

    if location:
        results = [
            profile for profile in results
            if location in profile["location"].lower()
        ]

    if selected_interests:
        results = [
            profile for profile in results
            if any(interest in profile["interests"] for interest in selected_interests)
        ]

    return jsonify(results)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    return render_template(
        "myprofile.html",
        google_maps_api_key=current_app.config.get("GOOGLE_MAPS_API_KEY", ""),
        is_logged_in=True
    )


@app.route("/profile/<int:profile_id>")
def profile_detail(profile_id):
    return f"Profile detail page for user {profile_id}"

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
