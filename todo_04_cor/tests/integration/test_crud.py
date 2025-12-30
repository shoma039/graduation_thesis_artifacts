import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime, timedelta

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_crud_flow_add_list_show_update_complete(monkeypatch, capsys):
    import src.storage.db as db_mod

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # patch storage to use in-memory DB
    db_mod.get_conn = lambda: conn

    # create schema
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

    # monkeypatch geocode to insert and return a location
    import src.services.geocode as geocode_mod

    def fake_geocode(name):
        c = conn.cursor()
        c.execute("INSERT INTO location (user_input_name, latitude, longitude, timezone, geocoded_at) VALUES (?,?,?,?,datetime('now'))", (name, 35.6895, 139.6917, 'Asia/Tokyo'))
        conn.commit()
        lid = c.lastrowid
        c.execute("SELECT * FROM location WHERE id = ?", (lid,))
        row = c.fetchone()
        return dict(row)

    monkeypatch.setattr(geocode_mod, "geocode_location", fake_geocode)

    # monkeypatch scheduler to return deterministic candidate
    import src.services.scheduler as scheduler_mod

    def fake_pick(loc, deadline_dt):
        cand = (datetime.utcnow().date() + timedelta(days=1)).isoformat()
        return {"date": cand, "precip": 0.0, "temp": 15.0}

    monkeypatch.setattr(scheduler_mod, "pick_candidate_date", fake_pick)

    # import CLI handlers
    import src.cli.commands.add as add_cmd
    import src.cli.commands.list_cmd as list_cmd
    import src.cli.commands.show as show_cmd
    import src.cli.commands.update as update_cmd
    import src.cli.commands.complete as complete_cmd

    # 1) Add
    a = SimpleNamespace()
    a.title = "CRUD テスト"
    a.deadline = "明日"
    a.location = "東京"
    a.priority = "高"
    a.json = False

    add_cmd.handle(a)
    out = capsys.readouterr().out
    assert "作成しました: ID=" in out

    # DB has one task
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM task")
    assert cur.fetchone()["c"] == 1

    # 2) List (ensure no exception)
    list_cmd.handle(SimpleNamespace())
    lout = capsys.readouterr().out
    assert "Tasks" in lout

    # 3) Show
    show_cmd.handle(SimpleNamespace(id=1))
    sout = capsys.readouterr().out
    assert "タイトル: CRUD テスト" in sout

    # 4) Update (change priority)
    u = SimpleNamespace()
    u.id = 1
    u.title = None
    u.deadline = "明後日"
    u.location = None
    u.priority = "中"
    update_cmd.handle(u)
    uout = capsys.readouterr().out
    assert "更新しました: 1" in uout

    # verify priority changed
    cur.execute("SELECT priority FROM task WHERE id = 1")
    assert cur.fetchone()["priority"] == "中"

    # 5) Complete
    complete_cmd.handle(SimpleNamespace(id=1))
    cout = capsys.readouterr().out
    assert "完了として削除しました: 1" in cout

    cur.execute("SELECT COUNT(*) as c FROM task")
    assert cur.fetchone()["c"] == 0
