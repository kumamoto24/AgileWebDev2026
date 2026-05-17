from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


# Decorator: constraints for new users who did not complete profile
def profile_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))

        profile = current_user.profile

        if not profile or not profile.is_complete:
            flash("Please complete your profile first.")
            return redirect(url_for("profiles.profile"))

        return view_func(*args, **kwargs)

    return wrapped_view
