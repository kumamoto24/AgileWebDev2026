from app.helpers import calculate_distance_km


def test_calculate_distance_km_between_perth_and_fremantle():
    perth_latitude = -31.9523
    perth_longitude = 115.8613
    fremantle_latitude = -32.0569
    fremantle_longitude = 115.7439

    distance = calculate_distance_km(
        perth_latitude,
        perth_longitude,
        fremantle_latitude,
        fremantle_longitude,
    )

    assert 15 <= distance <= 17
