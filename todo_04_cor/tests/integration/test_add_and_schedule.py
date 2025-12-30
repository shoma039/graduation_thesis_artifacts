import sqlite3
from types import SimpleNamespace
from datetime import datetime, timedelta, date
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_add_and_schedule_creates_task_and_outputs_candidate(monkeypatch, capsys):
    # Create in-memory DB and patch get_conn for storage and migrate
    import src.storage.db as db_mod
    import src.storage.migrate as migrate_mod

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Ensure the storage layer uses our in-memory connection
    db_mod.get_conn = lambda: conn

    # Create schema directly on the in-memory connection (avoid migrate closing it)
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS location (
        id INTEGER PRIMARY KEY,
        user_input_name TEXT,
        latitude REAL,
        longitude REAL,
        timezone TEXT,
        geocoded_at TEXT
    );
    CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        priority TEXT DEFAULT '中',
        location_id INTEGER,
        deadline_utc TEXT,
        candidate_date_local TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT,
        updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS forecastsample (
        id INTEGER PRIMARY KEY,
        location_id INTEGER,
        date_local TEXT,
        precip_probability REAL,
        temperature_c REAL,
        fetched_at TEXT
    );
    ''')
    conn.commit()

    # Patch geocode to return a deterministic location dict
    import src.services.geocode as geocode_mod
    geo_result = {
        "id": 1,
        "user_input_name": "東京",
        "latitude": 35.6895,
        "longitude": 139.6917,
        "timezone": "Asia/Tokyo",
    }

    monkeypatch.setattr(geocode_mod, "geocode_location", lambda name: geo_result)

    # Patch weather to return deterministic forecasts for the window
    import src.services.weather as weather_mod

    def fake_fetch_daily_forecast(lat, lon, start_date, end_date):
        # Normalize to date objects
        if hasattr(start_date, "strftime"):
            s = start_date
        else:
            s = datetime.fromisoformat(start_date).date()
        if hasattr(end_date, "strftime"):
            e = end_date
        else:
            e = datetime.fromisoformat(end_date).date()

        out = []
        d = s
        i = 0
        while d <= e:
            # create descending precip so middle day is best
            precip = float((i % 3) * 20)
            temp = 10.0 + i
            out.append({"date": d.isoformat(), "precip": precip, "temp": temp})
            d = d + timedelta(days=1)
            i += 1
        return out

    monkeypatch.setattr(weather_mod, "fetch_daily_forecast", fake_fetch_daily_forecast)
    # Patch scheduler to avoid DB collision-check that would close the shared conn
    import src.services.scheduler as scheduler_mod

    def fake_pick_candidate_date(loc, deadline_dt):
        # choose tomorrow as candidate for deterministic behavior
        cand_date = (datetime.utcnow().date() + timedelta(days=1)).isoformat()
        return {"date": cand_date, "precip": 0.0, "temp": 12.3}

    monkeypatch.setattr(scheduler_mod, "pick_candidate_date", fake_pick_candidate_date)

    # Use the add command handler directly
    import src.cli.commands.add as add_cmd

    # Build args similar to CLI
    args = SimpleNamespace()
    args.title = "テスト予定"
    args.deadline = "明日"
    args.location = "東京"
    args.priority = "中"
    args.json = False

    # Call handler
    add_cmd.handle(args)

    captured = capsys.readouterr()
    out = captured.out

    # Assert output contains expected Japanese summary
    assert "作成しました: ID=" in out
    assert "候補日:" in out

    # Ensure a task row exists in the DB
    cur = conn.cursor()
    cur.execute("SELECT * FROM task")
    rows = cur.fetchall()
    assert len(rows) == 1

    row = rows[0]
    assert row["title"] == "テスト予定"
    assert row["priority"] == "中"
    assert row["location_id"] == 1
