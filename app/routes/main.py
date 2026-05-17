from flask import Blueprint, current_app, render_template
from flask_login import current_user, login_required

from app.decorators import profile_required
from app.helpers import AGE_RANGES, ALL_INTERESTS, get_feature_profile


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/index")
def index():
    return render_template(
        "index.html",
        is_logged_in=False,
        profiles=get_feature_profile()
    )


@main_bp.route("/home")
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
