from flask import Blueprint, jsonify, redirect, render_template, request, url_for


main_bp = Blueprint("main", __name__, template_folder="templates")


PROFILES = [
    {
        "id": 1,
        "name": "Emily",
        "age": 22,
        "location": "Perth",
        "interests": ["Music", "Travel"],
        "distance": 4,
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&auto=format&fit=crop",
    },
    {
        "id": 2,
        "name": "Sophia",
        "age": 24,
        "location": "Sydney",
        "interests": ["Fitness", "Food"],
        "distance": 3929,
        "image": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800&auto=format&fit=crop",
    },
    {
        "id": 3,
        "name": "Alex",
        "age": 25,
        "location": "Melbourne",
        "interests": ["Movies", "Photography"],
        "distance": 2721,
        "image": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&auto=format&fit=crop",
    },
    {
        "id": 4,
        "name": "Mia",
        "age": 23,
        "location": "Perth",
        "interests": ["Art", "Reading", "Dancing"],
        "distance": 8,
        "image": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800&auto=format&fit=crop",
    },
]


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/home")
def home():
    return render_template("logined_homepage.html", username="Alex")


@main_bp.get("/matches")
def matches():
    return redirect(url_for("main.home"))


@main_bp.get("/messages")
def messages():
    return redirect(url_for("main.home"))


@main_bp.get("/profile")
def profile():
    return redirect(url_for("main.home"))


@main_bp.get("/login")
def login():
    return redirect(url_for("main.home"))


@main_bp.get("/api/health")
def api_health():
    return jsonify({"status": "ok", "message": "HeartLink API is running"})


@main_bp.route("/api/echo", methods=["GET", "POST"])
def api_echo():
    payload = request.get_json(silent=True) or {}
    return jsonify(
        {
            "method": request.method,
            "query": request.args.to_dict(flat=False),
            "json": payload,
        }
    )


@main_bp.get("/api/recommended-profiles")
def recommended_profiles():
    return jsonify(PROFILES)


@main_bp.get("/api/search-profiles")
def search_profiles():
    keyword = request.args.get("keyword", "").strip().lower()
    location = request.args.get("location", "").strip().lower()
    selected_interests = {
        interest.lower() for interest in request.args.getlist("interests") if interest
    }

    matching_profiles = []
    for profile in PROFILES:
        profile_interests = {interest.lower() for interest in profile["interests"]}
        matches_keyword = (
            not keyword
            or keyword in profile["name"].lower()
            or any(keyword in interest for interest in profile_interests)
        )
        matches_location = not location or location in profile["location"].lower()
        matches_interests = not selected_interests or selected_interests.intersection(
            profile_interests
        )

        if matches_keyword and matches_location and matches_interests:
            matching_profiles.append(profile)

    return jsonify(matching_profiles)


@main_bp.get("/profile/<int:profile_id>")
def profile_detail(profile_id):
    profile = next((item for item in PROFILES if item["id"] == profile_id), None)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404
    return jsonify(profile)
