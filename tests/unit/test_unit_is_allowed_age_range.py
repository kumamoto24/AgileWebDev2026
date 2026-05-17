from app.helpers import is_allowed_age_range


def test_is_allowed_age_range_allows_none_none():
    assert is_allowed_age_range(None, None) is True


def test_is_allowed_age_range_allows_exact_defined_range():
    assert is_allowed_age_range(18, 24) is True
    assert is_allowed_age_range(25, 34) is True
    assert is_allowed_age_range(35, 44) is True
    assert is_allowed_age_range(45, 54) is True
    assert is_allowed_age_range(55, None) is True


def test_is_allowed_age_range_rejects_unsupported_range():
    assert is_allowed_age_range(20, 24) is False
    assert is_allowed_age_range(18, 34) is False
    assert is_allowed_age_range(55, 64) is False
