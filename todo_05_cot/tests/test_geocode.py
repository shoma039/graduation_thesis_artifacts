def test_geocode_importable():
    from src.services import geocode
    assert hasattr(geocode, 'geocode_place')
