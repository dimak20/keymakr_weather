from weather_app.interfaces import DataValidator

class TemperatureValidator(DataValidator):
    def validate(self, data: dict) -> bool:
        temperature = data.get("temperature")

        return -50 <= temperature <= 50


class WeatherValidator:
    validators = [
        TemperatureValidator
    ]

    def __init__(self):
        self._validators = [validator() for validator in self.validators]

    def validate(self, data: dict) -> bool:
        for validator in self._validators:
            if not validator.validate(data=data):
                return False

        return True
