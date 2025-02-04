from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CityListSerializer(serializers.Serializer):
    cities = serializers.ListSerializer(
        child=serializers.CharField(max_length=100),
        allow_empty=False,
        help_text="List of cities ['Odesa', 'Київ', 'berlin']"
    )

    def validate_cities(self, cities):
        for city in cities:
            if not city.replace(" ", "").isalpha():
                raise ValidationError(f"Invalid city: {city}")
        return cities
