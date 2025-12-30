from src.storage.db import get_conn


def migrate():
    conn = get_conn()
    cur = conn.cursor()
    # Create tables according to data-model.md
    cur.execute('''
    CREATE TABLE IF NOT EXISTS location (
        id INTEGER PRIMARY KEY,
        user_input_name TEXT,
        latitude REAL,
        longitude REAL,
        timezone TEXT,
        geocoded_at TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        priority TEXT DEFAULT '中',
        location_id INTEGER,
        deadline_utc TEXT,
        candidate_date_local TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(location_id) REFERENCES location(id)
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS forecastsample (
        id INTEGER PRIMARY KEY,
        location_id INTEGER,
        date_local TEXT,
        precip_probability REAL,
        temperature_c REAL,
        fetched_at TEXT,
        FOREIGN KEY(location_id) REFERENCES location(id)
    )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
