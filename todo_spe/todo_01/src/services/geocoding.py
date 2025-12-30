from geopy.geocoders import Nominatim
from typing import List, Dict


def geocode_place(name: str, limit: int = 3) -> List[Dict]:
    """Return list of candidate places with name, latitude, longitude, display_name."""
    geolocator = Nominatim(user_agent="todo-weather-cli")
    try:
        results = geolocator.geocode(name, exactly_one=False, limit=limit, addressdetails=False)
    except Exception:
        return []
    if not results:
        return []
    out = []
    for r in results:
        out.append({
            "name": r.raw.get("display_name", r.address),
            "latitude": float(r.latitude),
            "longitude": float(r.longitude),
        })
    return out
