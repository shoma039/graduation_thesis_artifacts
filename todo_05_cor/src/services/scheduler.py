from typing import List, Dict, Optional
from datetime import date, datetime
from . import storage, weather
from ..utils import timezone as tzutils


def _date_str(dt: date) -> str:
    return dt.isoformat()


def _date_from_iso(iso: str) -> date:
    return datetime.fromisoformat(iso).date()


def generate_candidates_for_task(task_id: int, max_candidates: int = 1, max_reassign_attempts: int = 3) -> Dict:
    """Generate candidate dates for a single task and persist them.

    Basic algorithm:
    - Read task and its place (lat/lon/timezone) and deadline
    - Fetch daily forecast from today..deadline
    - Sort dates by precip_probability asc
    - Try to assign the best free date; if occupied, prefer earlier-registered task (don't evict)
    - If no free date found, return up to `max_candidates` alternative free dates (unassigned)

    Returns a dict with 'assigned' (list) and 'alternatives' (list)
    """
    task = storage.get_task(task_id)
    if not task:
        raise ValueError('task not found')

    if not task.get('deadline'):
        return {'assigned': [], 'alternatives': []}

    if not task.get('lat') or not task.get('lon'):
        return {'assigned': [], 'alternatives': []}

    # compute date range: from today in place tz to deadline date (inclusive)
    tz = task.get('timezone') or 'UTC'
    try:
        tzinfo = tzutils.ZoneInfo(tz)
        today_local = datetime.now(tz=tzinfo).date()
    except Exception:
        today_local = date.today()

    try:
        deadline_date = _date_from_iso(task['deadline'])
    except Exception:
        deadline_date = datetime.fromisoformat(task['deadline']).date()

    start_date = today_local
    end_date = deadline_date
    if start_date > end_date:
        return {'assigned': [], 'alternatives': []}

    start_iso = start_date.isoformat()
    end_iso = end_date.isoformat()

    forecasts = weather.get_daily_forecast(task['lat'], task['lon'], start_iso, end_iso, timezone=tz)
    if not forecasts:
        return {'assigned': [], 'alternatives': []}

    # sort by precip then by temp_max (ascending precip, descending temp_max)
    candidates = sorted(forecasts, key=lambda d: (d.get('precip_probability') if d.get('precip_probability') is not None else 9999, -(d.get('temp_max') if d.get('temp_max') is not None else 0)))

    assigned = []
    alternatives = []

    # attempt to assign
    attempts = 0
    for day in candidates:
        if len(assigned) >= max_candidates:
            break
        dstr = day['date']
        existing = storage.get_candidate_dates_on_date(dstr)
        if not existing:
            # free -> assign
            storage.insert_candidate_date(task_id, dstr, 0, day.get('precip_probability'), day.get('temp_max'))
            assigned.append({'date': dstr, 'precip': day.get('precip_probability'), 'temp': day.get('temp_max')})
        else:
            # conflict: check owner created_at, prefer earlier-registered (keep existing)
            # if any existing candidate is already confirmed, do not evict
            if any((int(e.get('is_confirmed') or 0) == 1) for e in existing):
                # cannot evict confirmed candidate
                pass
            else:
                earliest = min(existing, key=lambda r: r.get('created_at') or '')
                existing_created = earliest.get('created_at')
                task_created = task.get('created_at')
                try:
                    if existing_created and task_created and existing_created > task_created:
                        # current task was created earlier -> evict existing
                        evicted_task_id = earliest.get('task_id')
                        storage.delete_candidate_dates_for_task(evicted_task_id)
                        storage.insert_candidate_date(task_id, dstr, 0, day.get('precip_probability'), day.get('temp_max'))
                        assigned.append({'date': dstr, 'precip': day.get('precip_probability'), 'temp': day.get('temp_max')})
                    else:
                        # cannot evict, skip
                        pass
                except Exception:
                    pass

        attempts += 1
        if attempts >= (max_reassign_attempts * 5):
            break

    # if no assigned found, produce alternatives: up to max_candidates free dates
    if not assigned:
        for day in candidates:
            if len(alternatives) >= max_candidates:
                break
            dstr = day['date']
            existing = storage.get_candidate_dates_on_date(dstr)
            if not existing:
                alternatives.append({'date': dstr, 'precip': day.get('precip_probability'), 'temp': day.get('temp_max')})

    return {'assigned': assigned, 'alternatives': alternatives}
