from abc import ABC, abstractmethod

class WeatherProvider(ABC):
    @abstractmethod
    def get_region(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_temperature(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_condition(self, data: dict) -> str:
        pass

    @abstractmethod
    def build_request_params(self, city: str) -> dict:
        pass

    @abstractmethod
    def get_city_response(self, data: dict) -> dict:
        pass


class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: dict) -> bool:
        pass
