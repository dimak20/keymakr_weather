from unittest.mock import patch

from celery.result import AsyncResult
from django.test import TestCase
from faker.proxy import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from weather_app.tasks import logger
from weather_app.tests.tests_weather_api import WEATHER_BASE_URL

fake = Faker()


def task_status_url(task_id: str) -> str:
    return reverse("weather:task_status", args=[task_id])


def generate_city() -> str:
    return fake.city()


class TaskStatusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

    @patch("weather_app.views.AsyncResult")
    def test_task_status_complete(self, mock_async):
        mock_task = mock_async.return_value
        mock_task.info = {"status": "completed", "result": "some result"}
        mock_task.ready.return_value = True

        url = task_status_url("123")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["result"], "some result")

    @patch("weather_app.views.AsyncResult")
    def test_task_status_failed(self, mock_async):
        mock_task = mock_async.return_value
        mock_task.info = {"status": "failed", "errors": "some errors"}
        mock_task.ready.return_value = True

        url = task_status_url("123")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "failed")
        self.assertEqual(response.data["errors"], "some errors")

    @patch("weather_app.views.AsyncResult")
    def test_task_status_not_found(self, mock_async):
        mock_task = mock_async.return_value
        mock_task.info = None
        mock_task.ready.return_value = False

        url = task_status_url("123")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, "Task with id 123 does not exist")

    def test_task_status_integration(self):
        city = "Berlin"
        payload = {
            "cities": [city]
        }
        response = self.client.post(
            WEATHER_BASE_URL,
            data=payload,
            content_type="application/json"
        )

        task_id = response.data.get("task_id")
        self.assertIsNotNone(task_id)

        task_result = AsyncResult(task_id)
        task_result.get(timeout=10)

        url = task_status_url(task_id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")
        self.assertIn("results", response.data)

        response_city_data = response.data.get("results", {}).get("Europe", {})[0]

        self.assertIn("temperature", response_city_data)
        self.assertIn("description", response_city_data)
