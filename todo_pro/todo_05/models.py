from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class Location:
    name: str
    latitude: float
    longitude: float
    timezone: str

@dataclass
class Task:
    id: int
    title: str
    done: bool
    priority: int
    location: Optional[Location]
    deadline: Optional[str]
    candidate_date: Optional[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.location is not None:
            d['location'] = asdict(self.location)
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Task':
        loc = None
        if d.get('location'):
            l = d['location']
            loc = Location(name=l['name'], latitude=l['latitude'], longitude=l['longitude'], timezone=l['timezone'])
        return Task(
            id=d['id'],
            title=d['title'],
            done=d.get('done', False),
            priority=d.get('priority', 2),
            location=loc,
            deadline=d.get('deadline'),
            candidate_date=d.get('candidate_date'),
            created_at=d.get('created_at', datetime.utcnow().isoformat())
        )
