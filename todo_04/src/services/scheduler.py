from datetime import datetime, timedelta
from src.services import weather
from src.storage import db


def pick_candidate_date(location, deadline_dt):
    # location: dict with latitude, longitude, timezone, id
    # deadline_dt: datetime object
    # For simplicity: look 0..(deadline date) inclusive, pick day with min precip
    lat = location.get("latitude")
    lon = location.get("longitude")
    if lat is None or lon is None:
        return None

    today = datetime.utcnow().date()
    end = deadline_dt.date()
    if end < today:
        return None

    forecasts = weather.fetch_daily_forecast(lat, lon, today, end)
    if not forecasts:
        return None

    # find min precip
    best = None
    for f in forecasts:
        if f.get('precip') is None:
            continue
        if best is None or f['precip'] < best['precip']:
            best = f

    if not best:
        # pick earliest available date as fallback
        best = forecasts[0]

    # collision avoidance: ensure candidate date not already used by other tasks
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM task WHERE candidate_date_local = ?", (best['date'],))
    row = cur.fetchone()
    if row:
        # simple strategy: pick next best that is not used
        for f in forecasts:
            cur.execute("SELECT id FROM task WHERE candidate_date_local = ?", (f['date'],))
            if not cur.fetchone():
                best = f
                break

    conn.close()
    return best
