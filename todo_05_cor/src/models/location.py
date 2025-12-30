from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Location:
    id: Optional[int]
    display_name: str
    lat: Optional[float]
    lon: Optional[float]
    timezone: Optional[str]

    @staticmethod
    def from_row(row: Any) -> Optional['Location']:
        if row is None:
            return None
        return Location(
            id=row['id'],
            display_name=row.get('display_name'),
            lat=row.get('lat'),
            lon=row.get('lon'),
            timezone=row.get('timezone'),
        )
