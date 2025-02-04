from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geo_normalizer")


def normalize_city(city: str) -> str:
    location = geolocator.geocode(city, language="en")
    return location.address if location else None
