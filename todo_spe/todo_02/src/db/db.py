import sqlite3
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "todo.db"

def connect(path: Optional[str] = None):
    # Use the current DB_PATH when no explicit path is provided. We avoid
    # binding DB_PATH at function-definition time so tests can override the
    # module-level `DB_PATH` and have `connect()` pick up the new value.
    if path is None:
        path = DB_PATH

    # Do not enable PARSE_DECLTYPES to avoid sqlite3 attempting to convert
    # timestamp-like strings (which may be date-only) into datetime objects.
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    ensure_migrations(conn)
    return conn

def ensure_migrations(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            latitude REAL,
            longitude REAL,
            timezone TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            priority TEXT,
            location_id INTEGER,
            due_date TIMESTAMP,
            candidate_date TIMESTAMP,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY,
            location_id INTEGER,
            date TEXT,
            precipitation_prob REAL,
            temp_min REAL,
            temp_max REAL,
            fetched_at TIMESTAMP
        )
        """
    )
    conn.commit()

def ensure_location(conn: sqlite3.Connection, loc: dict) -> int:
    cur = conn.cursor()
    # check existing by name and coords
    cur.execute(
        "SELECT id FROM locations WHERE name = ? AND latitude = ? AND longitude = ?",
        (loc.get("name"), loc.get("latitude"), loc.get("longitude")),
    )
    row = cur.fetchone()
    if row:
        return int(row["id"])
    cur.execute(
        "INSERT INTO locations (name, latitude, longitude, timezone) VALUES (?, ?, ?, ?)",
        (loc.get("name"), loc.get("latitude"), loc.get("longitude"), loc.get("timezone")),
    )
    conn.commit()
    return cur.lastrowid

def _to_iso(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    if isinstance(dt, datetime):
        # ensure timezone-aware; if naive, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    return str(dt)


def insert_task(conn: sqlite3.Connection, title: str, priority: str, location_id: int, due_date, candidate_date: Optional[object]) -> int:
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    due_iso = _to_iso(due_date)
    cand_iso = _to_iso(candidate_date)
    cur.execute(
        "INSERT INTO tasks (title, completed, priority, location_id, due_date, candidate_date, created_at, updated_at) VALUES (?, 0, ?, ?, ?, ?, ?, ?)",
        (title, priority, location_id, due_iso, cand_iso, now, now),
    )
    conn.commit()
    return cur.lastrowid

def get_task(conn: sqlite3.Connection, task_id: int):
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return cur.fetchone()

def list_tasks(conn: sqlite3.Connection, sort: str = "date"):
    cur = conn.cursor()
    order = "due_date"
    if sort == "priority":
        order = "priority"
    elif sort == "created":
        order = "created_at"
    cur.execute(f"SELECT * FROM tasks ORDER BY {order} ASC")
    return cur.fetchall()

def update_task(conn: sqlite3.Connection, task_id: int, updates: dict):
    cur = conn.cursor()
    fields = []
    values = []
    for k, v in updates.items():
        fields.append(f"{k} = ?")
        values.append(v)
    # convert any datetime-like updates to ISO
    for i, val in enumerate(values):
        if isinstance(val, datetime):
            if val.tzinfo is None:
                val = val.replace(tzinfo=timezone.utc)
            values[i] = val.isoformat()

    updated_at = datetime.now(timezone.utc).isoformat()
    values.append(updated_at)
    values.append(task_id)
    sql = f"UPDATE tasks SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    cur.execute(sql, values)
    conn.commit()

def delete_task(conn: sqlite3.Connection, task_id: int):
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
