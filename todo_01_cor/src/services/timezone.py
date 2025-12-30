from timezonefinder import TimezoneFinder
from typing import Optional


def timezone_for(lat: float, lon: float) -> Optional[str]:
    tf = TimezoneFinder()
    try:
        tz = tf.timezone_at(lng=lon, lat=lat)
        return tz
    except Exception:
        return None
