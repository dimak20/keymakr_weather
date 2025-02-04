from django.conf import settings

from weather_app.interfaces import WeatherProvider, WeatherAPIProvider

weather_source = settings.WEATHER_API_URL


class WeatherProviderFactory:
    @staticmethod
    def create_provider() -> WeatherProvider:
        if "weatherapi" in weather_source:
            return WeatherAPIProvider()
        else:
            raise ValueError("Unsupported weather data source")
