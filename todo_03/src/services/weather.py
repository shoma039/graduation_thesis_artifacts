import requests
from datetime import date
from typing import List, Dict


def fetch_daily_weather(lat: float, lon: float, start: date, end: date, timezone: str) -> List[Dict]:
    """Fetch daily precipitation probability and temperature from Open-Meteo (no API key). Returns list per date."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_probability_max,temperature_2m_max",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": timezone,
    }
    headers = {"User-Agent": "todo-cli-scheduler/1.0 (contact: example)"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    j = r.json()
    daily = j.get("daily", {})
    dates = daily.get("time", [])
    precs = daily.get("precipitation_probability_max", [])
    temps = daily.get("temperature_2m_max", [])
    out = []
    for i, d in enumerate(dates):
        out.append({
            "date": d,
            "precipitation_probability": (precs[i] if i < len(precs) else None),
            "temperature": (temps[i] if i < len(temps) else None),
        })
    return out
