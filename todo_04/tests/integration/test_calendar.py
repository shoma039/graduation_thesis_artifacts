import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timedelta, date

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_calendar_shows_task_dates_and_locations(capsys):
    import src.storage.db as db_mod

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    db_mod.get_conn = lambda: conn

    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE location (id INTEGER PRIMARY KEY, user_input_name TEXT, latitude REAL, longitude REAL, timezone TEXT, geocoded_at TEXT);
    CREATE TABLE task (id INTEGER PRIMARY KEY, title TEXT NOT NULL, priority TEXT DEFAULT '中', location_id INTEGER, deadline_utc TEXT, candidate_date_local TEXT, status TEXT DEFAULT 'open', created_at TEXT, updated_at TEXT);
    CREATE TABLE forecastsample (id INTEGER PRIMARY KEY, location_id INTEGER, date_local TEXT, precip_probability REAL, temperature_c REAL, fetched_at TEXT);
    ''')
    conn.commit()

    # Insert a location and a task with candidate date in December 2025
    cdate = (datetime.utcnow().date() + timedelta(days=2)).isoformat()
    cur.execute("INSERT INTO location (user_input_name, latitude, longitude, timezone, geocoded_at) VALUES (?,?,?,?,datetime('now'))", ("東京", 35.6895, 139.6917, 'Asia/Tokyo'))
    lid = cur.lastrowid
    cur.execute("INSERT INTO task (title, priority, location_id, deadline_utc, candidate_date_local, created_at, updated_at) VALUES (?,?,?,?,?,datetime('now'),datetime('now'))", ("カレンダー・テスト", '中', lid, datetime.utcnow().isoformat(), cdate))
    conn.commit()

    # Optionally insert a forecastsample row (calendar currently doesn't display it, but ensure available)
    cur.execute("INSERT INTO forecastsample (location_id, date_local, precip_probability, temperature_c, fetched_at) VALUES (?,?,?,?,datetime('now'))", (lid, cdate, 10.0, 12.5))
    conn.commit()

    # Call calendar handler for the month containing cdate
    import src.cli.commands.calendar as calendar_cmd

    month = cdate[:7]
    calendar_cmd.handle(SimpleNamespace(month=month))
    out = capsys.readouterr().out

    assert f"Calendar {month}" in out
    assert "カレンダー・テスト" in out
    assert cdate in out
