from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Task:
    id: Optional[int]
    title: str
    completed: bool
    priority: str
    place_id: Optional[int]
    deadline: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    @staticmethod
    def from_row(row: Any) -> Optional['Task']:
        if row is None:
            return None
        return Task(
            id=row['id'],
            title=row['title'],
            completed=bool(row['completed']),
            priority=row.get('priority'),
            place_id=row.get('place_id'),
            deadline=row.get('deadline'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
        )
