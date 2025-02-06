from django.conf import settings

from weather_app.base import WeatherProvider
from weather_app.services import WeatherAPIProvider, WeatherVisualCrossingAPIProvider

weather_source = settings.WEATHER_URL


class WeatherProviderFactory:
    @staticmethod
    def create_provider() -> WeatherProvider:
        if "weatherapi" in weather_source:
            return WeatherAPIProvider()

        if "visualcrossing" in weather_source:
            return WeatherVisualCrossingAPIProvider()

        raise ValueError("Unsupported weather data source")
