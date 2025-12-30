import datetime
from src.db import db
from src.services import scheduler, weather


def test_select_skips_taken_date(monkeypatch, tmp_path):
    # Setup in-memory DB
    conn = db.connect(':memory:')

    # Ensure location
    loc = {"name": "札幌", "latitude": 43.06, "longitude": 141.34, "timezone": "Asia/Tokyo"}
    loc_id = db.ensure_location(conn, loc)

    today = datetime.date.today()
    # create two forecast days: day0 and day1
    day0 = (today + datetime.timedelta(days=1)).isoformat()
    day1 = (today + datetime.timedelta(days=2)).isoformat()

    # monkeypatch forecasts: day0 lower precip than day1
    monkeypatch.setattr(weather, 'fetch_daily_forecast', lambda lat, lon, start, end, timezone='UTC': [
        {"date": day0, "precipitation_prob": 10.0},
        {"date": day1, "precipitation_prob": 20.0},
    ])

    # Insert an existing task that already took day0 for this location
    db.insert_task(conn, "既存", "medium", loc_id, datetime.datetime.now(datetime.timezone.utc), day0)

    # Now select candidate: should skip day0 and choose day1
    due_dt = datetime.datetime.combine(today + datetime.timedelta(days=2), datetime.datetime.min.time())
    chosen = scheduler.select_candidate_for_location(conn, loc_id, due_dt)
    assert chosen == day1


def test_propose_alternative_after_due(monkeypatch):
    conn = db.connect(':memory:')
    loc = {"name": "札幌", "latitude": 43.06, "longitude": 141.34, "timezone": "Asia/Tokyo"}
    loc_id = db.ensure_location(conn, loc)

    today = datetime.date.today()
    # due window has two days but both occupied; alternative is the next free day
    d0 = (today + datetime.timedelta(days=1)).isoformat()
    d1 = (today + datetime.timedelta(days=2)).isoformat()
    d2 = (today + datetime.timedelta(days=3)).isoformat()

    # forecasts from today+1 .. today+3
    monkeypatch.setattr(weather, 'fetch_daily_forecast', lambda lat, lon, start, end, timezone='UTC': [
        {"date": d0}, {"date": d1}, {"date": d2}
    ])

    # occupy d0 and d1
    db.insert_task(conn, "t0", "medium", loc_id, datetime.datetime.now(datetime.timezone.utc), d0)
    db.insert_task(conn, "t1", "medium", loc_id, datetime.datetime.now(datetime.timezone.utc), d1)

    due_dt = datetime.datetime.combine(today + datetime.timedelta(days=2), datetime.datetime.min.time())
    alt = scheduler.propose_alternative_date(conn, loc_id, due_dt, max_days=5)
    assert alt == d2
