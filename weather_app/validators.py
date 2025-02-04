class WeatherDataValidator:
    @staticmethod
    def is_valid_temperature(temperature: float) -> bool:
        return -50 <= temperature <= 50
