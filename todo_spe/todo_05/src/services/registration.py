from typing import Optional, Tuple, Dict
from . import date_parser, geocode, storage, validation
from ..lib.errors import ValidationError, ExternalAPIError


def register_task(title: str, deadline_text: Optional[str], place_query: Optional[str], priority: str = 'medium', place_candidate: Optional[Dict] = None) -> Tuple[int, Optional[Dict]]:
    """Register a task: validate inputs, resolve place, parse deadline, persist location and task.

    Returns (task_id, location_dict)
    """
    # basic validation
    validation.require_title(title)

    place = None
    place_id = None
    if place_candidate:
        place = place_candidate
        place_id = storage.insert_location(place.get('display_name'), place.get('lat'), place.get('lon'), place.get('timezone') or 'UTC')
    elif place_query:
        candidates = geocode.geocode_place(place_query, limit=1)
        if not candidates:
            raise ExternalAPIError('場所のジオコーディングに失敗しました')
        place = candidates[0]
        place_id = storage.insert_location(place.get('display_name'), place.get('lat'), place.get('lon'), place.get('timezone') or 'UTC')

    # parse deadline
    deadline_iso = None
    if deadline_text:
        tz = place.get('timezone') if place else 'UTC'
        dt_iso = date_parser.parse_natural_date_iso(deadline_text, tz)
        if dt_iso is None:
            raise ValidationError('期限の解析に失敗しました')
        deadline_iso = dt_iso

    tid = storage.insert_task(title, priority, place_id, deadline_iso)
    return tid, place
