from app.helpers import compatible


class ProfileStub:
    def __init__(self, gender, orientation):
        self.gender = gender
        self.orientation = orientation


def test_compatible_straight_male_with_straight_female():
    current = ProfileStub(gender="Male", orientation="Straight")
    candidate = ProfileStub(gender="Female", orientation="Straight")

    assert compatible(current, candidate) is True


def test_compatible_straight_male_with_straight_male():
    current = ProfileStub(gender="Male", orientation="Straight")
    candidate = ProfileStub(gender="Male", orientation="Straight")

    assert compatible(current, candidate) is False


def test_compatible_straight_female_with_straight_male():
    current = ProfileStub(gender="Female", orientation="Straight")
    candidate = ProfileStub(gender="Male", orientation="Straight")

    assert compatible(current, candidate) is True


def test_compatible_straight_female_with_straight_female():
    current = ProfileStub(gender="Female", orientation="Straight")
    candidate = ProfileStub(gender="Female", orientation="Straight")

    assert compatible(current, candidate) is False


def test_compatible_gay_with_gay():
    current = ProfileStub(gender="Male", orientation="Gay")
    candidate = ProfileStub(gender="Male", orientation="Gay")

    assert compatible(current, candidate) is True


def test_compatible_gay_with_straight():
    current = ProfileStub(gender="Male", orientation="Gay")
    candidate = ProfileStub(gender="Male", orientation="Straight")

    assert compatible(current, candidate) is False


def test_compatible_lesbian_with_lesbian():
    current = ProfileStub(gender="Female", orientation="Lesbian")
    candidate = ProfileStub(gender="Female", orientation="Lesbian")

    assert compatible(current, candidate) is True


def test_compatible_other_allows_any_orientation():
    current = ProfileStub(gender="Female", orientation="Other")
    candidate = ProfileStub(gender="Male", orientation="Straight")

    assert compatible(current, candidate) is True
