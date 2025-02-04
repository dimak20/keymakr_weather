from urllib.parse import urljoin

from django.conf import settings
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

from weather_app.validators import WeatherValidator

geolocator = Nominatim(user_agent="geo_normalizer", adapter_factory=AioHTTPAdapter)
weather_validator = WeatherValidator()


async def normalize_city(city: str) -> str:
    location = await geolocator.geocode(city, language="en", timeout=20)
    return location.address.split(",")[0] if location else None


def validate_weather_response(data: dict) -> bool:
    return weather_validator.validate(data=data)


def generate_json_link(file_path: str) -> str:
    file_path = file_path.replace(settings.WEATHER_DATA_DIR, "")
    return urljoin(settings.MEDIA_HOST, f"{settings.MEDIA_URL}{file_path.lstrip('/')}")
