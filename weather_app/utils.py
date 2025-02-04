from geopy.geocoders import Nominatim

from weather_app.validators import WeatherValidator

geolocator = Nominatim(user_agent="geo_normalizer")
weather_validator = WeatherValidator()


def normalize_city(city: str) -> str:
    location = geolocator.geocode(city, language="en")
    return location.address.split(",")[0] if location else None


def validate_weather_response(data: dict) -> bool:
    return weather_validator.validate(data=data)
