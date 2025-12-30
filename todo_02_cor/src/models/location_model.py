from dataclasses import dataclass

@dataclass
class Location:
    id: int
    name: str
    latitude: float
    longitude: float
    timezone: str
