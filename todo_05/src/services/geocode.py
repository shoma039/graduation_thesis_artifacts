from typing import List, Dict, Optional
import httpx
from .cache import Cache
from datetime import date

_cache = Cache('geocode')


def _get_timezone_from_open_meteo(lat: float, lon: float) -> Optional[str]:
    # Query Open-Meteo to obtain the timezone string for the point
    url = 'https://api.open-meteo.com/v1/forecast'
    today = date.today().isoformat()
    params = {
        'latitude': lat,
        'longitude': lon,
        'hourly': 'temperature_2m',
        'start_date': today,
        'end_date': today,
    }
    try:
        r = httpx.get(url, params=params, timeout=10.0)
        r.raise_for_status()
        j = r.json()
        return j.get('timezone')
    except Exception:
        return None


def geocode_place(query: str, limit: int = 5) -> List[Dict]:
    """Return a list of candidate places with lat/lon/timezone (if resolvable).

    Each item: {display_name, lat, lon, timezone}
    """
    key = f"geocode:{query}"
    cached = _cache.get(key)
    if cached:
        return cached

    url = 'https://nominatim.openstreetmap.org/search'
    params = {'q': query, 'format': 'jsonv2', 'limit': limit, 'addressdetails': 1}
    headers = {'User-Agent': 'todo-weather-scheduler/1.0 (+https://example.local)'}
    try:
        r = httpx.get(url, params=params, headers=headers, timeout=10.0)
        r.raise_for_status()
        items = r.json()
    except Exception:
        items = []

    results = []
    for it in items:
        try:
            lat = float(it.get('lat'))
            lon = float(it.get('lon'))
        except Exception:
            continue
        display_name = it.get('display_name') or f"{lat},{lon}"
        tz = _get_timezone_from_open_meteo(lat, lon)
        results.append({'display_name': display_name, 'lat': lat, 'lon': lon, 'timezone': tz})

    _cache.set(key, results)
    return results
