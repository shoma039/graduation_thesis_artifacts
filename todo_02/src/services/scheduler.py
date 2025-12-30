from datetime import datetime, timedelta, date
from typing import Optional
from src.services import weather


def select_candidate_for_location(conn, location_id: int, due_dt: datetime) -> Optional[str]:
    """Select a candidate date (ISO YYYY-MM-DD) for the given location and due datetime.

    Policy (T025):
    - Within the window from today..due_date, pick the day with lowest precipitation probability
      that does NOT already have a task assigned for the same `location_id` (先着順).
    - If all good days are occupied, return None to signal no available candidate inside the window
      (caller may then ask for a post-due alternative — T026).
    """
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude, timezone FROM locations WHERE id = ?", (location_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Location not found")
    lat = row["latitude"]
    lon = row["longitude"]
    tz = row["timezone"] or "UTC"

    # Search window: from today up to and including the due date
    start = date.today()
    end = due_dt.date()
    if start > end:
        # If due date is in the past relative to today, just use due_date as single-day window
        start = end

    # Use weather service with caching support when available. Some tests monkeypatch
    # `fetch_daily_forecast` without the `conn`/`location_id` kwargs, so attempt a
    # call with caching and fall back to a plain call if the target doesn't accept
    # those parameters.
    try:
        forecasts = weather.fetch_daily_forecast(lat, lon, start, end, timezone=tz, conn=conn, location_id=location_id)
    except TypeError:
        forecasts = weather.fetch_daily_forecast(lat, lon, start, end, timezone=tz)
    if not forecasts:
        return None

    # Sort candidate days by precipitation probability (ascending), then by date (ascending)
    def sort_key(f):
        p = f.get("precipitation_prob")
        if p is None:
            p = 999.0
        return (p, f.get("date"))

    sorted_forecasts = sorted(forecasts, key=sort_key)

    for f in sorted_forecasts:
        cand_date = f.get("date")  # ISO string like 'YYYY-MM-DD'
        if not cand_date:
            continue

        # Check whether any task already has this candidate_date for the same location
        # Use SQLite date(...) wrapper to compare date portion safely
        cur.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE date(candidate_date) = ? AND location_id = ?",
            (cand_date, location_id),
        )
        row = cur.fetchone()
        taken = int(row["cnt"]) if row else 0
        if taken == 0:
            return cand_date

    # No free day found within the due-date window
    return None


def propose_alternative_date(conn, location_id: int, due_dt: datetime, max_days: int = 30) -> Optional[str]:
    """When no free candidate exists before or on the due date, search after the due date
    for the earliest available day (up to `max_days` after due date).

    Returns ISO date string or None if no free day found within the window.
    """
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude, timezone FROM locations WHERE id = ?", (location_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("Location not found")
    lat = row["latitude"]
    lon = row["longitude"]
    tz = row["timezone"] or "UTC"

    start = due_dt.date() + timedelta(days=1)
    end = due_dt.date() + timedelta(days=max_days)

    forecasts = weather.fetch_daily_forecast(lat, lon, start, end, timezone=tz)
    if not forecasts:
        return None

    # Prefer earliest date that is not taken (first-come availability)
    # We'll iterate by ascending date
    sorted_by_date = sorted(forecasts, key=lambda f: f.get("date"))
    for f in sorted_by_date:
        cand_date = f.get("date")
        if not cand_date:
            continue
        cur.execute(
            "SELECT COUNT(*) as cnt FROM tasks WHERE date(candidate_date) = ? AND location_id = ?",
            (cand_date, location_id),
        )
        r = cur.fetchone()
        taken = int(r["cnt"]) if r else 0
        if taken == 0:
            return cand_date

    return None
