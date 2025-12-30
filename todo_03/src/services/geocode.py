import requests
from typing import Dict


def geocode_place(name: str) -> Dict:
    """Use Open-Meteo geocoding API (no API key) to resolve place name to lat/lon/timezone."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": name, "count": 1, "language": "ja", "format": "json"}
    headers = {"User-Agent": "todo-cli-scheduler/1.0 (contact: example)"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    j = r.json()
    results = j.get("results")
    if not results:
        raise ValueError("都市名を解決できませんでした。別の名称を試してください。")
    first = results[0]
    return {
        "name": first.get("name") or name,
        "latitude": float(first["latitude"]),
        "longitude": float(first["longitude"]),
        "timezone": first.get("timezone") or "UTC",
    }
