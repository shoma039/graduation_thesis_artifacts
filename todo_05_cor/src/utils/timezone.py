from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Tuple


def to_timezone(dt: datetime, tz_str: str) -> datetime:
    """Return datetime converted to timezone `tz_str`.

    - If `dt` is naive, assume it is UTC.
    - Result is timezone-aware with tzinfo set to ZoneInfo(tz_str).
    """
    if dt is None:
        raise ValueError('dt is required')
    # If naive, assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = timezone.utc
    return dt.astimezone(tz)


def to_utc(dt: datetime) -> datetime:
    """Convert aware or naive datetime to UTC (tz-aware result).

    If `dt` is naive, it's assumed to be in local system tz? For safety, assume UTC.
    """
    if dt is None:
        raise ValueError('dt is required')
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def local_day_range_utc(d: date, tz_str: str) -> Tuple[datetime, datetime]:
    """Return (start_utc, end_utc) datetimes covering the local date `d` in timezone `tz_str`.

    `start_utc` is the UTC instant at local midnight (00:00) of date `d`.
    `end_utc` is the UTC instant at local 23:59:59.999999 of date `d` (exclusive end may be start of next day).
    """
    tz = None
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = timezone.utc

    local_start = datetime.combine(d, time.min).replace(tzinfo=tz)
    local_end = datetime.combine(d, time.max).replace(tzinfo=tz)
    start_utc = local_start.astimezone(timezone.utc)
    end_utc = local_end.astimezone(timezone.utc)
    return start_utc, end_utc


def next_local_midnight_utc(dt: datetime, tz_str: str) -> datetime:
    """Given any datetime `dt`, return the UTC instant of the next local midnight in `tz_str`.

    Useful to compute upper bounds for ranges.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = timezone.utc
    loc = dt.astimezone(tz)
    next_day = (loc + timedelta(days=1)).date()
    next_mid_local = datetime.combine(next_day, time.min).replace(tzinfo=tz)
    return next_mid_local.astimezone(timezone.utc)
