import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / 'data.sqlite3'

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY,
        display_name TEXT NOT NULL,
        lat REAL,
        lon REAL,
        timezone TEXT
    );
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        priority TEXT DEFAULT 'medium',
        place_id INTEGER,
        deadline TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(place_id) REFERENCES locations(id)
    );
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS candidate_dates (
        id INTEGER PRIMARY KEY,
        task_id INTEGER,
        date TEXT,
        is_confirmed INTEGER DEFAULT 0,
        expected_precipitation REAL,
        expected_temperature REAL,
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print(f"Initialized DB at {DB_PATH}")
