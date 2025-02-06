from abc import ABC, abstractmethod

class WeatherProvider(ABC):
    @abstractmethod
    def get_region(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_temperature(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_description(self, data: dict) -> str:
        pass

    @abstractmethod
    def build_request_url(self, city: str) -> str:
        pass

    @abstractmethod
    def get_city_response(self, data: dict) -> dict:
        pass


class DataValidator(ABC):
    @abstractmethod
    def validate(self, data: dict) -> bool:
        pass
