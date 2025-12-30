import requests
from datetime import date, datetime, timezone
from typing import List, Dict, Optional
import sqlite3

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def _rows_to_forecasts(rows):
    out = []
    for r in rows:
        out.append({
            "date": r["date"],
            "precipitation_prob": r["precipitation_prob"],
            "temp_min": r["temp_min"],
            "temp_max": r["temp_max"],
        })
    return out


def fetch_daily_forecast(lat: float, lon: float, start_date: date, end_date: date, timezone: str = "UTC", conn: Optional[sqlite3.Connection] = None, location_id: Optional[int] = None) -> List[Dict]:
    """Fetch daily forecast for range. If `conn` and `location_id` are provided, attempt to read cached forecasts
    from the `forecasts` table; otherwise call the external API and persist results when possible.
    """
    # If DB caching available, try to retrieve cached rows
    if conn is not None and location_id is not None:
        cur = conn.cursor()
        cur.execute(
            "SELECT date, precipitation_prob, temp_min, temp_max FROM forecasts WHERE location_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC",
            (location_id, start_date.isoformat(), end_date.isoformat()),
        )
        rows = cur.fetchall()
        if rows and len(rows) >= ((end_date - start_date).days + 1):
            return _rows_to_forecasts(rows)

    # Fallback to API request
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_mean",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": timezone,
    }
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    prec = daily.get("precipitation_probability_mean", [])
    tmin = daily.get("temperature_2m_min", [])
    tmax = daily.get("temperature_2m_max", [])
    out = []
    for i, d in enumerate(dates):
        entry = {
            "date": d,
            "precipitation_prob": float(prec[i]) if i < len(prec) else None,
            "temp_min": float(tmin[i]) if i < len(tmin) else None,
            "temp_max": float(tmax[i]) if i < len(tmax) else None,
        }
        out.append(entry)

        # persist to DB cache if possible
        if conn is not None and location_id is not None:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO forecasts (location_id, date, precipitation_prob, temp_min, temp_max, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                (location_id, d, entry["precipitation_prob"], entry["temp_min"], entry["temp_max"], datetime.now(timezone.utc).isoformat()),
            )
    if conn is not None and location_id is not None:
        conn.commit()

    return out
