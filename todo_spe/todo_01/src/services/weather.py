import requests
from typing import Dict, Any, Optional
from datetime import date, timedelta


def get_daily_weather(lat: float, lon: float, start_date: date, end_date: date, timezone: str = "UTC") -> Dict[str, Dict[str, Optional[float]]]:
    """Fetch daily precipitation probability max and temperature (mean) from Open-Meteo for date range.

    Returns mapping date_str -> {"precipitation_probability": float (0-100), "temperature": float}
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_probability_max,temperature_2m_max,temperature_2m_min",
        "timezone": timezone,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    daily = j.get("daily", {})
    dates = daily.get("time", [])
    precip = daily.get("precipitation_probability_max", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    out = {}
    for i, d in enumerate(dates):
        p = precip[i] if i < len(precip) else None
        # average temp
        temp = None
        if i < len(tmax) and i < len(tmin):
            try:
                temp = (tmax[i] + tmin[i]) / 2.0
            except Exception:
                temp = None
        out[d] = {
            "precipitation_probability": p,
            "temperature": temp,
        }
    return out
