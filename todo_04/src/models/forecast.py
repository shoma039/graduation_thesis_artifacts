from src.storage import db


def add_forecast_sample(location_id, date_local, precip_probability, temperature_c):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO forecastsample (location_id, date_local, precip_probability, temperature_c, fetched_at) VALUES (?,?,?,?,datetime('now'))",
        (location_id, date_local, precip_probability, temperature_c),
    )
    conn.commit()
    fid = cur.lastrowid
    conn.close()
    return fid


def get_forecasts(location_id, start_date=None, end_date=None):
    conn = db.get_conn()
    cur = conn.cursor()
    if start_date and end_date:
        cur.execute(
            "SELECT * FROM forecastsample WHERE location_id = ? AND date_local BETWEEN ? AND ? ORDER BY date_local",
            (location_id, start_date, end_date),
        )
    else:
        cur.execute("SELECT * FROM forecastsample WHERE location_id = ? ORDER BY date_local", (location_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
