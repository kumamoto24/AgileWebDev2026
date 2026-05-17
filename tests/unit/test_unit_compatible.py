from app.routes import compatible


class ProfileStub:
    def __init__(self, gender, orientation):
        self.gender = gender
        self.orientation = orientation


def test_compatible_straight_male_with_straight_female():
    current = ProfileStub(gender="male", orientation="straight")
    candidate = ProfileStub(gender="female", orientation="straight")

    assert compatible(current, candidate) is True


def test_compatible_straight_male_with_straight_male():
    current = ProfileStub(gender="male", orientation="straight")
    candidate = ProfileStub(gender="male", orientation="straight")

    assert compatible(current, candidate) is False


def test_compatible_straight_female_with_straight_male():
    current = ProfileStub(gender="female", orientation="straight")
    candidate = ProfileStub(gender="male", orientation="straight")

    assert compatible(current, candidate) is True


def test_compatible_straight_female_with_straight_female():
    current = ProfileStub(gender="female", orientation="straight")
    candidate = ProfileStub(gender="female", orientation="straight")

    assert compatible(current, candidate) is False


def test_compatible_gay_with_gay():
    current = ProfileStub(gender="male", orientation="gay")
    candidate = ProfileStub(gender="male", orientation="gay")

    assert compatible(current, candidate) is True


def test_compatible_gay_with_straight():
    current = ProfileStub(gender="male", orientation="gay")
    candidate = ProfileStub(gender="male", orientation="straight")

    assert compatible(current, candidate) is False


def test_compatible_lesbian_with_lesbian():
    current = ProfileStub(gender="female", orientation="lesbian")
    candidate = ProfileStub(gender="female", orientation="lesbian")

    assert compatible(current, candidate) is True


def test_compatible_other_allows_any_orientation():
    current = ProfileStub(gender="female", orientation="other")
    candidate = ProfileStub(gender="male", orientation="straight")

    assert compatible(current, candidate) is True
