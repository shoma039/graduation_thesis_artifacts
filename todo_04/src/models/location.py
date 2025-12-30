from src.storage import db


def create_location(user_input_name, latitude, longitude, timezone=None):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO location (user_input_name, latitude, longitude, timezone, geocoded_at) VALUES (?,?,?,?,datetime('now'))",
        (user_input_name, latitude, longitude, timezone),
    )
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return lid


def get_location_by_id(location_id):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM location WHERE id = ?", (location_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def find_cached_location_by_name(name):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM location WHERE user_input_name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
