import logging
from time import sleep

import requests
from celery import shared_task
from django.conf import settings

from weather_app.factories import WeatherProviderFactory
from weather_app.utils import normalize_city, validate_weather_response

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def fetch_weather_data(self, cities: list[str]) -> dict | None:
    results = {}
    total_cities = len(cities)
    task_id = self.request.id
    provider = WeatherProviderFactory.create_provider()
    self.update_state(
        state="running",
        meta=
        {
            "status": "running",
            "task_id": task_id,
            "progress": f"0 / {total_cities}"
        }
    )

    sleep(10)
    for index, city in enumerate(cities, start=1):
        city_normalized = normalize_city(city)

        if not city_normalized:
            raise ValueError(f"Cannot normalize city: {city}")

        params = provider.build_request_params(city)
        sleep(10)
        try:
            response = requests.get(
                settings.WEATHER_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            logger.info(data)
            city_params = provider.get_city_response(data=data)

            if not validate_weather_response(data=city_params):
                continue

            region = city_params["region"]

            if region not in results:
                results[region] = []

            results[region].append(city_params)
            self.update_state(
                state="running",
                meta={
                    "status": "running",
                    "task_id": task_id,
                    "progress": f"{index} / {total_cities}"
                }
            )
        except requests.exceptions.RequestException as e:
            logger.warning(
                f"Error fetching data from weather API: {city}: {e}"
            )
    return {"status": "completed", "data": results}
