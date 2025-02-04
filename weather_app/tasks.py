import json
import logging
import os.path

import requests
from celery import shared_task
from django.conf import settings

from weather_app.factories import WeatherProviderFactory
from weather_app.utils import normalize_city, validate_weather_response, generate_json_link

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def fetch_weather_data(self, cities: list[str]) -> dict | None:
    results = {}
    file_paths = []
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

    for index, city in enumerate(cities, start=1):
        city_normalized = normalize_city(city)

        if not city_normalized:
            raise ValueError(f"Cannot normalize city: {city}")

        params = provider.build_request_params(city)
        try:
            response = requests.get(
                settings.WEATHER_URL,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            city_params = {"city": city_normalized}
            city_params.update(provider.get_city_response(data=data))

            if not validate_weather_response(data=city_params):
                continue

            region = city_params.pop("region", None)

            if region and region not in results:
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

    for region, region_data in results.items():
        dir_path = os.path.join(settings.WEATHER_DATA_DIR, region)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"task_{task_id}.json")

        with open(file_path, "w") as f:
            json.dump(region_data, f, indent=4)

        json_link = generate_json_link(file_path)
        file_paths.append(json_link)

    return {
        "status": "completed",
        "results": {
            region: data for region, data in results.items()
        },
        "files": file_paths
    }
