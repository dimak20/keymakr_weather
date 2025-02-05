import asyncio
import json
import logging
import os.path

import httpx
from celery import shared_task
from celery.exceptions import Ignore
from django.conf import settings

from weather_app.exceptions import NotNormalizedException
from weather_app.factories import WeatherProviderFactory
from weather_app.utils import normalize_city, validate_weather_response, generate_json_link

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def fetch_weather_data(self, cities: list[str]) -> dict | None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(fetch_data(self, cities))
    except NotNormalizedException as e:
        logger.error(f"Task {self.request.id} failed due to city normalization error: {e}")
        self.update_state(state="failed", meta={"status": "failed", "errors": str(e)})
        raise Ignore()


async def fetch_data(self, cities: list[str]) -> dict | None:
    results = {}
    file_paths = []
    total_cities = len(cities)
    task_id = self.request.id
    provider = WeatherProviderFactory.create_provider()

    self.update_state(
        state="running",
        meta={"status": "running", "task_id": task_id, "processed_cities": 0, "progress": f"0 / {total_cities}"}
    )

    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_city_weather(self, client, provider, city, total_cities)
            for city in cities
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    for index, (city, result) in enumerate(zip(cities, responses), start=1):
        if isinstance(result, Exception):
            logger.warning(f"Error fetching data for {city}: {result}")
            continue

        city_params = result
        region = city_params.pop("region", None)

        if region and region not in results:
            results[region] = []

        results[region].append(city_params)

    for region, region_data in results.items():
        dir_path = os.path.join(settings.WEATHER_DATA_DIR, region)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"task_{task_id}.json")

        with open(file_path, "w") as f:
            json.dump(region_data, f, indent=4)

        json_link = generate_json_link(file_path)
        file_paths.append(json_link)

    return {"status": "completed", "results": results, "files": file_paths}


async def fetch_city_weather(self, client, provider, city: str, total_cities: int) -> dict:
    city_normalized = normalize_city(city)
    task_result = self.AsyncResult(self.request.id)
    current_processed_cities = task_result.info.get("processed_cities", 0)

    if not city_normalized:
        raise NotNormalizedException(f"Cannot normalize city {city}")

    progress = round(((current_processed_cities + 1) / total_cities * 100), 2)
    self.update_state(
        state="running",
        meta={
            "status": "running",
            "task_id": self.request.id,
            "processed_cities": current_processed_cities + 1,
            "progress": f"{progress}%"
        }
    )

    params = provider.build_request_params(city)

    try:
        response = await client.get(settings.WEATHER_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        city_params = {"city": city_normalized}
        city_params.update(provider.get_city_response(data=data))

        if not validate_weather_response(data=city_params):
            logger.warning(f"Invalid weather data for {city}")

        return city_params

    except httpx.RequestError as e:
        raise logger.warning(f"Error fetching weather for {city}: {e}")

@shared_task(bind=True)
def fetch_region_data(self, region: str) -> list[dict] | None:
    self.update_state(
        state="running"
    )
    region = region.capitalize()
