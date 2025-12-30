from datetime import datetime, date, time, timezone
from zoneinfo import ZoneInfo
from typing import Union


def to_utc(dt: datetime, tzname: str) -> datetime:
    """Convert a naive or timezone-aware local datetime to UTC timezone-aware datetime."""
    if dt.tzinfo is None:
        local = dt.replace(tzinfo=ZoneInfo(tzname))
    else:
        local = dt.astimezone(ZoneInfo(tzname))
    return local.astimezone(ZoneInfo("UTC"))


def from_utc_to_local(utc_dt: Union[datetime, str], tzname: str) -> datetime:
    """Convert a UTC datetime (or ISO string) to local timezone-aware datetime."""
    if isinstance(utc_dt, str):
        utc = datetime.fromisoformat(utc_dt)
    else:
        utc = utc_dt
    if utc.tzinfo is None:
        utc = utc.replace(tzinfo=ZoneInfo("UTC"))
    return utc.astimezone(ZoneInfo(tzname))


def local_date_to_utc_iso(local_date: Union[date, str], tzname: str) -> str:
    """Given a local date (YYYY-MM-DD or date), return ISO UTC datetime string at local midnight.

    This is useful for storing deadlines that are specified as local dates.
    """
    if isinstance(local_date, str):
        d = date.fromisoformat(local_date)
    else:
        d = local_date
    local_dt = datetime.combine(d, time.min)
    utc_dt = to_utc(local_dt, tzname)
    return utc_dt.replace(tzinfo=ZoneInfo("UTC")).isoformat()


def isoformat_utc(dt: datetime) -> str:
    """Return an ISO 8601 string in UTC for the given datetime."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo("UTC")).isoformat()
