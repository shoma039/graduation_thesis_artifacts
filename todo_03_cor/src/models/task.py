from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, date

from ..models.location import Location


@dataclass
class CandidateDate:
    date: str  # ISO date string YYYY-MM-DD
    precipitation_probability: Optional[float] = None
    temperature: Optional[float] = None
    reason: Optional[str] = None


@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    priority: str = "medium"
    location: Optional[Location] = None
    due_date: Optional[str] = None  # local date string
    candidate_dates: List[CandidateDate] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
