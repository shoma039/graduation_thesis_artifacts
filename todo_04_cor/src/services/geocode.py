import requests
from src.storage import db


def geocode_location(name):
    # try to find existing cached location
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM location WHERE user_input_name = ?", (name,))
    row = cur.fetchone()
    if row:
        return dict(row)

    # Nominatim API (no API key) - limited usage
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": name, "format": "json", "limit": 1}
    headers = {"User-Agent": "todo-cli-weather/1.0 (+https://example)"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data:
        return None
    first = data[0]
    lat = float(first.get("lat"))
    lon = float(first.get("lon"))
    # timezone lookup omitted here; store empty and fill later if needed
    cur.execute(
        "INSERT INTO location (user_input_name, latitude, longitude, timezone, geocoded_at) VALUES (?,?,?,?,datetime('now'))",
        (name, lat, lon, None),
    )
    conn.commit()
    loc_id = cur.lastrowid
    cur.execute("SELECT * FROM location WHERE id = ?", (loc_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
