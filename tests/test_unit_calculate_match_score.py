from app.routes import calculate_match_score


class CandidateStub:
    def __init__(self, bio=None, profile_image_path=None, interests=None):
        self.bio = bio
        self.profile_image_path = profile_image_path
        self.interests = interests or []


def test_calculate_match_score_with_no_shared_interests_and_no_distance():
    candidate = CandidateStub()

    score = calculate_match_score(
        shared_interest_count=0,
        distance=None,
        candidate=candidate,
    )

    assert score == 0


def test_calculate_match_score_adds_interest_score_up_to_cap():
    candidate = CandidateStub()

    score = calculate_match_score(
        shared_interest_count=5,
        distance=None,
        candidate=candidate,
    )

    assert score == 30


def test_calculate_match_score_distance_scores_correctly():
    candidate = CandidateStub()

    assert calculate_match_score(0, 2, candidate) == 60
    assert calculate_match_score(0, 7, candidate) == 55
    assert calculate_match_score(0, 15, candidate) == 50
    assert calculate_match_score(0, 30, candidate) == 35
    assert calculate_match_score(0, 80, candidate) == 20
    assert calculate_match_score(0, 200, candidate) == 5
    assert calculate_match_score(0, 800, candidate) == 0


def test_calculate_match_score_includes_candidate_completeness_points():
    candidate = CandidateStub(
        bio="Hello",
        profile_image_path="uploads/profile_images/test.png",
        interests=["Music", "Sports"],
    )

    score = calculate_match_score(
        shared_interest_count=1,
        distance=10,
        candidate=candidate,
    )

    expected_interest_score = 10
    expected_distance_score = 55
    expected_completeness_score = 3 + 3 + 4

    assert score == expected_interest_score + expected_distance_score + expected_completeness_score
