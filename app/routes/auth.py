import requests
from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_user, logout_user

from app import db
from app.helpers import get_feature_profile
from app.models import Profile, User


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not email or not password or not confirm_password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Please complete all required fields.",
                site_key=current_app.config["RECAPTCHA_SITE_KEY"]
            )

        if len(password) < 8 or len(password) > 64:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Password must be between 8 and 64 characters.",
                site_key=current_app.config["RECAPTCHA_SITE_KEY"]
            )

        if password != confirm_password:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Passwords do not match.",
                site_key=current_app.config["RECAPTCHA_SITE_KEY"]
            )

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template(
                "signup.html",
                is_logged_in=False,
                signup_error="Email already registered.",
                site_key=current_app.config["RECAPTCHA_SITE_KEY"]
            )

        captcha_response = request.form.get("g-recaptcha-response")
        secret_key = current_app.config["RECAPTCHA_SECRET_KEY"]

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
                site_key=current_app.config["RECAPTCHA_SITE_KEY"]
            )

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        new_profile = Profile(
            id=new_user.id,
            user_id=new_user.id
        )
        db.session.add(new_profile)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("profiles.profile"))

    return render_template(
        "signup.html",
        is_logged_in=False,
        site_key=current_app.config["RECAPTCHA_SITE_KEY"]
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            return render_template(
                "index.html",
                is_logged_in=False,
                show_login_modal=True,
                login_error="Please enter both email and password."
            )

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return render_template(
                "index.html",
                is_logged_in=False,
                show_login_modal=True,
                login_error="Invalid email or password."
            )

        remember = request.form.get("remember") == "on"
        login_user(user, remember=remember)

        return redirect(url_for("main.home"))

    return render_template(
        "index.html",
        is_logged_in=False,
        profiles=get_feature_profile(),
        show_login_modal=True
    )


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("main.index"))
