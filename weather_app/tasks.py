import logging

from celery import shared_task
from django.conf import settings
import requests

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def fetch_weather_data(cities: list[str], task_id: str):
    results = {}

    for city in cities:
        params = {
            "q": city,
            "key": settings.WEATHER_API_KEY
        }

        try:
            response = requests.get(
                settings.WEATHER_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            logger.info(data)
            results[city] = city

        except requests.exceptions.RequestException as e:
            logger.warning(
                f"Error fetching data from weather API: {city}: {e}"
            )
    return results
