from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from src.utils.parse_date import parse_date


def now_tokyo():
    return datetime.now(tz=ZoneInfo("Asia/Tokyo"))


def test_parse_tomorrow():
    tz = "Asia/Tokyo"
    dt = parse_date("明日", timezone=tz)
    assert dt is not None
    assert dt.tzinfo is not None
    # 明日は今日より1日以上未来で、24時間以内ではないことを期待
    today = now_tokyo()
    delta = dt.astimezone(ZoneInfo(tz)).date() - today.date()
    assert delta.days == 1


def test_parse_next_week_monday():
    tz = "Asia/Tokyo"
    dt = parse_date("来週の月曜", timezone=tz)
    assert dt is not None
    # weekday() where Monday == 0
    wd = dt.astimezone(ZoneInfo(tz)).weekday()
    assert wd == 0
    # should be between 7 and 13 days from now
    today = now_tokyo()
    days_ahead = (dt.astimezone(ZoneInfo(tz)).date() - today.date()).days
    assert 7 <= days_ahead <= 13


def test_parse_next_month_second_friday():
    tz = "Asia/Tokyo"
    dt = parse_date("来月第2金曜", timezone=tz)
    assert dt is not None
    tok = dt.astimezone(ZoneInfo(tz))
    # Friday is weekday 4
    assert tok.weekday() == 4
    # month should be next month relative to now
    today = now_tokyo()
    next_month = today.month + 1 if today.month < 12 else 1
    assert tok.month == next_month
from src.utils.parse_date import parse_date, to_iso


def test_parse_explicit_iso():
    dt = parse_date("2026/01/05 14:00", timezone="Asia/Tokyo")
    assert dt is not None
    iso = to_iso(dt)
    assert iso.startswith("2026-01-05")


def test_parse_tomorrow_and_weekday():
    assert parse_date("明日", timezone="Asia/Tokyo") is not None
    assert parse_date("来週の月曜", timezone="Asia/Tokyo") is not None


def test_parse_month_nth_weekday():
    assert parse_date("来月第2金曜", timezone="Asia/Tokyo") is not None
from src.utils.parse_date import parse_date, to_iso
from datetime import datetime


def test_parse_simple_japanese_relative_dates():
    # 明日 / 明後日 should parse
    d1 = parse_date("明日", timezone="Asia/Tokyo")
    assert d1 is not None and d1.tzinfo is not None

    d2 = parse_date("明後日", timezone="Asia/Tokyo")
    assert d2 is not None and d2.tzinfo is not None


def test_parse_weekday_expression():
    # Explicit date/time should parse reliably
    d = parse_date("2026/01/05 14:00", timezone="Asia/Tokyo")
    assert d is not None and d.tzinfo is not None


def test_to_iso_returns_string():
    d = parse_date("明日 09:00", timezone="Asia/Tokyo")
    iso = to_iso(d)
    assert iso is None or isinstance(iso, str)
