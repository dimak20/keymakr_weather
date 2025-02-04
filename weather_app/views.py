import uuid

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_app.serializers import CityListSerializer


class WeatherView(APIView):
    @extend_schema(
        request=CityListSerializer,
        responses={202: {"task_id": str}},
        description="Fetch a list of cities and returns task_id to check task status "
    )
    def post(self, request):
        serializer = CityListSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cities = serializer.validated_data["cities"]
        task_id = str(uuid.uuid4())
        fetch_weather_data.apply_async(args=[cities, task_id])

        return Response({"task_id": task_id}, status=status.HTTP_202_ACCEPTED)
