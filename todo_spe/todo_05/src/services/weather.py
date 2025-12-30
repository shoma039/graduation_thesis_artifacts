from typing import List, Dict, Optional
import httpx


def get_daily_forecast(lat: float, lon: float, start_date: str, end_date: str, timezone: str = 'UTC') -> List[Dict]:
    """Fetch daily forecast from Open-Meteo.

    Returns list of dicts: {date, precip_probability, temp_max, temp_min}
    Dates are strings YYYY-MM-DD.
    """
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_mean',
        'start_date': start_date,
        'end_date': end_date,
        'timezone': timezone,
    }
    try:
        r = httpx.get(url, params=params, timeout=15.0)
        r.raise_for_status()
        j = r.json()
    except Exception:
        return []

    daily = j.get('daily', {})
    dates = daily.get('time', [])
    precip = daily.get('precipitation_probability_mean', [])
    tmax = daily.get('temperature_2m_max', [])
    tmin = daily.get('temperature_2m_min', [])

    results: List[Dict] = []
    for i, d in enumerate(dates):
        results.append({
            'date': d,
            'precip_probability': float(precip[i]) if i < len(precip) else None,
            'temp_max': float(tmax[i]) if i < len(tmax) else None,
            'temp_min': float(tmin[i]) if i < len(tmin) else None,
        })
    return results
