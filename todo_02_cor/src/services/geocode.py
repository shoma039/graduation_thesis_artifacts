import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode_location(name: str) -> dict:
    params = {"name": name, "count": 1, "language": "ja"}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        raise ValueError(f"ジオコーディングで場所が見つかりませんでした: {name}")
    item = results[0]
    return {
        "name": item.get("name"),
        "latitude": float(item.get("latitude")),
        "longitude": float(item.get("longitude")),
        "timezone": item.get("timezone", "UTC"),
    }
