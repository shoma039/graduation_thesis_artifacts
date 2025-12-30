import requests
from typing import Optional, Tuple

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast'

def geocode_city(name: str) -> Optional[Tuple[str, float, float, str]]:
    """都市名を緯度・経度・表示名・タイムゾーンで返す（タイムゾーンは Open-Meteo で取得）。"""
    params = {'q': name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'todo-cli-app/1.0 (example)'}
    try:
        r = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        arr = r.json()
        if not arr:
            return None
        item = arr[0]
        lat = float(item['lat'])
        lon = float(item['lon'])
        display = item.get('display_name', name)
        # get timezone from Open-Meteo
        wp = {'latitude': lat, 'longitude': lon, 'current_weather': True}
        wr = requests.get(OPEN_METEO_BASE, params=wp, timeout=10)
        wr.raise_for_status()
        wj = wr.json()
        tz = wj.get('timezone', 'UTC')
        return (display, lat, lon, tz)
    except Exception:
        return None
