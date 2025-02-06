from django.test import TestCase
from faker.proxy import Faker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

fake = Faker()
WEATHER_BASE_URL = reverse("weather:weather_cities")


def generate_city() -> str:
    return fake.city()


class WeatherTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

    def test_response_contains_task_id(self):
        city = generate_city()
        payload = {
            "cities": [city]
        }

        response = self.client.post(
            WEATHER_BASE_URL,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_202_ACCEPTED
        )
        self.assertIn(
            "task_id",
            response.data
        )
        self.assertTrue(
            response.data.get("task_id")
        )

    def test_correct_response_with_list_of_cities(self):
        city_1 = generate_city()
        city_2 = generate_city()
        payload = {
            "cities": [
                city_1, city_2
            ]
        }

        response = self.client.post(
            WEATHER_BASE_URL,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code, status.HTTP_202_ACCEPTED
        )
        self.assertIn(
            "task_id",
            response.data
        )
        self.assertTrue(
            response.data.get("task_id")
        )

    def test_city_contains_digits(self):
        city = "Kiev1"
        payload = {
            "cities": [city]
        }

        response = self.client.post(
            WEATHER_BASE_URL,
            data=payload,
            content_type="application/json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
