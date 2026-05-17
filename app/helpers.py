import os
from math import atan2, cos, radians, sin, sqrt

from flask import current_app, url_for

from app import db
from app.models import Likes, Profile


ALL_INTERESTS = [
    "Sports",
    "Music",
    "Movies",
    "Travel",
    "Gaming",
    "Reading",
    "Cooking",
    "Fitness",
    "Art",
    "Technology",
]

AGE_RANGES = [
    {"label": "18-24", "min": 18, "max": 24},
    {"label": "25-34", "min": 25, "max": 34},
    {"label": "35-44", "min": 35, "max": 44},
    {"label": "45-54", "min": 45, "max": 54},
    {"label": "55+", "min": 55, "max": None},
]


def is_allowed_age_range(min_age, max_age):
    if min_age is None and max_age is None:
        return True

    for age_range in AGE_RANGES:
        matching_min_age = age_range["min"] == min_age
        matching_max_age = age_range["max"] == max_age

        if matching_min_age and matching_max_age:
            return True

    return False


def build_profile_image_url(image_path):
    if not image_path:
        return url_for("static", filename="images/default-profile.png")

    if image_path.startswith(("http://", "https://")):
        return image_path

    static_prefix = "/static/"
    if image_path.startswith(static_prefix):
        filename = image_path[len(static_prefix):]
    else:
        filename = image_path

    full_path = os.path.join(current_app.static_folder, filename)

    if not os.path.exists(full_path):
        return url_for("static", filename="images/default-profile.png")

    return url_for("static", filename=image_path)


def build_story_image_url(image_path):
    default_story_image = "images/default-story.jpg"

    if not image_path:
        return url_for("static", filename=default_story_image)

    if image_path.startswith(("http://", "https://")):
        return image_path

    static_prefix = "/static/"
    if image_path.startswith(static_prefix):
        filename = image_path[len(static_prefix):]
    else:
        filename = image_path

    full_path = os.path.join(current_app.static_folder, filename)

    if not os.path.exists(full_path):
        return url_for("static", filename=default_story_image)

    return url_for("static", filename=filename)


def build_story_slots(stories, slot_count=3):
    stories_by_order = {}

    for story in stories:
        if story.display_order and 1 <= story.display_order <= slot_count:
            stories_by_order[story.display_order] = story

    story_slots = []
    for display_order in range(1, slot_count + 1):
        story = stories_by_order.get(display_order)

        if story:
            story_slots.append({
                "title": story.title,
                "description": story.description,
                "image_url": build_story_image_url(story.image_path),
                "display_order": display_order,
                "is_empty": False,
            })
        else:
            story_slots.append({
                "title": "Add Story",
                "description": "Share a moment from your life.",
                "image_url": build_story_image_url(None),
                "display_order": display_order,
                "is_empty": True,
            })

    return story_slots


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


def get_feature_profile():
    featured_profiles = (
        Profile.query
        .outerjoin(Likes, Likes.liked_id == Profile.id)
        .filter(
            Profile.display_name.isnot(None),
            Profile.display_name != "",
            Profile.age.isnot(None),
            Profile.gender.isnot(None),
            Profile.gender != "",
            Profile.orientation.isnot(None),
            Profile.orientation != "",
            Profile.location_text.isnot(None),
            Profile.location_text != "",
            Profile.latitude.isnot(None),
            Profile.longitude.isnot(None),
            Profile.place_id.isnot(None),
            Profile.place_id != "",
            Profile.interests.any(),
        )
        .group_by(Profile.id)
        .order_by(db.func.count(Likes.id).desc(), Profile.id.asc())
        .limit(3)
        .all()
    )
    return [profile_to_card(profile) for profile in featured_profiles]


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

    if current_orientation == "gay":
        return candidate_orientation == "gay"

    if current_orientation == "lesbian":
        return candidate_orientation == "lesbian"

    return True


def calculate_match_score(shared_interest_count, distance, candidate):
    interest_score = min(shared_interest_count * 10, 30)

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

    completeness_score = 0

    if candidate.bio:
        completeness_score += 3

    if candidate.profile_image_path:
        completeness_score += 3

    if candidate.interests:
        completeness_score += 4

    return interest_score + distance_score + completeness_score
