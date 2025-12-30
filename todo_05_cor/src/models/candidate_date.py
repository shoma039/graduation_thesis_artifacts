from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class CandidateDate:
    id: Optional[int]
    task_id: int
    date: str
    is_confirmed: bool
    expected_precipitation: Optional[float]
    expected_temperature: Optional[float]

    @staticmethod
    def from_row(row: Any) -> Optional['CandidateDate']:
        if row is None:
            return None
        return CandidateDate(
            id=row['id'],
            task_id=row['task_id'],
            date=row.get('date'),
            is_confirmed=bool(row.get('is_confirmed', 0)),
            expected_precipitation=row.get('expected_precipitation'),
            expected_temperature=row.get('expected_temperature'),
        )
