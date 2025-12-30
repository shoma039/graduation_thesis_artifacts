from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: Optional[int]
    title: str
    completed: bool
    priority: str
    location_id: int
    due_date: datetime
    candidate_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
