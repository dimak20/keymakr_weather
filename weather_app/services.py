from django.conf import settings

from weather_app.base import WeatherProvider


class WeatherAPIProvider(WeatherProvider):
    def get_region(self, data: dict) -> str:
        return data["location"]["tz_id"].split("/")[0]

    def get_temperature(self, data: dict) -> float:
        return data["current"]["temp_c"]

    def get_description(self, data: dict) -> str:
        return data["current"]["condition"]["text"]

    def build_request_params(self, city: str) -> dict:
        return {
            "q": city,
            "key": settings.WEATHER_API_KEY
        }

    def get_city_response(self, data: dict) -> dict:
        return {
            "region": self.get_region(data),
            "temperature": self.get_temperature(data),
            "description": self.get_description(data)
        }
