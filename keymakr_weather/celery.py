import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "keymakr_weather.settings")

celery_app = Celery("keymakr_weather")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
