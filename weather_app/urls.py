from django.urls import path

from weather_app.views import WeatherView, TaskStatusView

app_name = "weather"

urlpatterns = [
    path("weather/", WeatherView.as_view(), name="weather_cities"),
    path("tasks/<str:task_id>/", TaskStatusView.as_view(), name="task_status"),
]
