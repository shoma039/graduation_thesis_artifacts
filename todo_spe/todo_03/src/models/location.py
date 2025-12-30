from dataclasses import dataclass


@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: str
