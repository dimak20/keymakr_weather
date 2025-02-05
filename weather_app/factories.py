from django.conf import settings

from weather_app.base import WeatherProvider
from weather_app.services import WeatherAPIProvider

weather_source = settings.WEATHER_URL


class WeatherProviderFactory:
    @staticmethod
    def create_provider() -> WeatherProvider:
        if "weatherapi" in weather_source:
            return WeatherAPIProvider()

        raise ValueError("Unsupported weather data source")
