from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.decorators import profile_required
from app.helpers import (
    build_profile_image_url,
    calculate_distance_km,
    calculate_match_score,
    compatible,
    is_allowed_age_range,
    profile_to_card,
)
from app.models import Interest, Profile


discovery_bp = Blueprint("discovery", __name__)


@discovery_bp.route("/api/recommended-profiles")
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


@discovery_bp.route("/api/search-profiles", methods=["GET"])
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

        if not compatible(current_profile, profile):
            continue

        if search_latitude is not None and search_longitude is not None:
            distance_from_search_location = calculate_distance_km(
                search_latitude,
                search_longitude,
                profile.latitude,
                profile.longitude
            )

            if distance_from_search_location > radius_km:
                continue

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
