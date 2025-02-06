from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from weather_app.serializers import CityListSerializer, RegionCityListSerializer
from weather_app.tasks import fetch_weather_data, fetch_region_data


class WeatherView(APIView):
    @extend_schema(
        request=CityListSerializer,
        responses={
            202: "Task ID"
        },
        description="Fetch a list of cities and returns task_id to check task status "
    )
    def post(self, request):
        serializer = CityListSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cities = serializer.validated_data["cities"]
        task = fetch_weather_data.apply_async(args=[cities])

        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class TaskStatusView(APIView):
    def get(self, request, task_id: str):
        result = AsyncResult(task_id)
        meta = result.info

        if not result.info:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data=f"Task with id {task_id} does not exist"
            )

        if isinstance(meta, Exception):
            meta = {
                "status": "failed",
                "errors": str(meta)
            }

        return Response(
            status=status.HTTP_200_OK,
            data=meta
        )


class RegionCitiesView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="region",
                type=str,
                location=OpenApiParameter.PATH,
                description="Region name (e.g., 'Europe', 'Asia', 'America')",
            )
        ],
        responses={200: RegionCityListSerializer},
        description="Fetch a list of cities from selected region"
    )
    def get(self, request, region: str):
        task = fetch_region_data.apply_async(args=[region])
        result = task.get(propagate=False)

        if isinstance(result, Exception):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "errors": str(result)
                }
            )

        return Response({"results": result}, status=status.HTTP_200_OK)
