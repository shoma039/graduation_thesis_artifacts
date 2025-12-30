import requests
from datetime import datetime, timedelta


def fetch_daily_forecast(lat, lon, start_date, end_date):
    # Open-Meteo daily API: temperature_2m_max/min and precipitation_probability_mean
    # start_date and end_date: date or ISO strings (YYYY-MM-DD)
    s = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)
    e = end_date.strftime("%Y-%m-%d") if hasattr(end_date, 'strftime') else str(end_date)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": s,
        "end_date": e,
        "daily": "precipitation_probability_mean,temperature_2m_max,temperature_2m_min",
        "timezone": "UTC",
    }
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return None
    j = r.json()
    daily = j.get("daily", {})
    dates = daily.get("time", [])
    precs = daily.get("precipitation_probability_mean", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    out = []
    for i, d in enumerate(dates):
        out.append({
            "date": d,
            "precip": precs[i] if i < len(precs) else None,
            "temp": ((tmax[i] + tmin[i]) / 2) if i < len(tmax) and i < len(tmin) else None,
        })
    return out
