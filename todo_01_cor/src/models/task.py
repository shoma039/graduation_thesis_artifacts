from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class CandidateDate:
    date: str  # ISO date
    precipitation_probability: Optional[float] = None
    temperature: Optional[float] = None
    reason: Optional[str] = None


@dataclass
class Location:
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None


@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    priority: str = "中"
    location: Optional[Location] = None
    due_date: Optional[str] = None  # ISO datetime with tz if available
    candidate_dates: List[CandidateDate] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # convert nested dataclasses
        if self.location:
            d["location"] = asdict(self.location)
        d["candidate_dates"] = [asdict(c) for c in self.candidate_dates]
        return d

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        loc = None
        if d.get("location"):
            locd = d["location"]
            loc = Location(**locd)
        cands = []
        for c in d.get("candidate_dates", []):
            cands.append(CandidateDate(**c))
        return Task(
            id=d["id"],
            title=d.get("title", ""),
            completed=d.get("completed", False),
            priority=d.get("priority", "中"),
            location=loc,
            due_date=d.get("due_date"),
            candidate_dates=cands,
            created_at=d.get("created_at", datetime.utcnow().isoformat()),
            updated_at=d.get("updated_at", datetime.utcnow().isoformat()),
        )
