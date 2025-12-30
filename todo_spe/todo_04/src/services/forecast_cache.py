from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.storage import db
from src.services import weather


def _parse_sqlite_ts(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        # SQLite 'datetime('now')' format -> 'YYYY-MM-DD HH:MM:SS'
        return datetime.fromisoformat(ts_str)
    except Exception:
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None


def get_cached_forecasts(location_id: int, start_date: str, end_date: str, max_age_hours: int = 6) -> Optional[List[Dict]]:
    """Return cached forecasts for `location_id` between `start_date` and `end_date` if fresh.

    - start_date/end_date: ISO date strings 'YYYY-MM-DD' or date-like strings accepted by SQL.
    - max_age_hours: max age of cached samples; if any sample is older, returns None.
    """
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM forecastsample WHERE location_id = ? AND date_local BETWEEN ? AND ? ORDER BY date_local",
        (location_id, start_date, end_date),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None

    now = datetime.utcnow()
    max_age = timedelta(hours=max_age_hours)

    results = []
    for r in rows:
        fetched_at = _parse_sqlite_ts(r["fetched_at"]) if "fetched_at" in r.keys() else None
        if fetched_at is None or (now - fetched_at) > max_age:
            # stale
            return None
        results.append({
            "date": r["date_local"],
            "precip": r["precip_probability"],
            "temp": r["temperature_c"],
        })

    return results


def bulk_insert_forecasts(location_id: int, forecasts: List[Dict]) -> None:
    """Insert multiple forecast samples into `forecastsample` table.

    `forecasts` is a list of dicts with keys: `date` (YYYY-MM-DD), `precip`, `temp`.
    """
    if not forecasts:
        return
    conn = db.get_conn()
    cur = conn.cursor()
    rows = []
    for f in forecasts:
        rows.append((location_id, f.get("date"), f.get("precip"), f.get("temp"), datetime.utcnow().isoformat()))

    cur.executemany(
        "INSERT INTO forecastsample (location_id, date_local, precip_probability, temperature_c, fetched_at) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def fetch_or_cache_forecast(location_id: int, lat: float, lon: float, start_date: str, end_date: str, max_age_hours: int = 6) -> List[Dict]:
    """Return forecasts for range [start_date, end_date].

    - Try cache first; if missing or stale, fetch from `weather.fetch_daily_forecast`, store and return.
    """
    cached = get_cached_forecasts(location_id, start_date, end_date, max_age_hours=max_age_hours)
    if cached is not None:
        return cached

    # fetch fresh
    fresh = weather.fetch_daily_forecast(lat, lon, start_date, end_date)
    if not fresh:
        # if fetch failed but stale cache existed, return stale? For now, return empty list
        return []

    # Insert into DB
    bulk_insert_forecasts(location_id, fresh)
    return fresh


def clear_old_forecasts(older_than_days: int = 30) -> int:
    """Delete forecasts older than `older_than_days`. Returns deleted row count."""
    cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM forecastsample WHERE fetched_at < ?", (cutoff.isoformat(),))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted
