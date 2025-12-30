import dateparser
from dateutil import tz
from datetime import datetime
from typing import Optional


def parse_natural_date(text: str, timezone: Optional[str] = None) -> datetime:
    """Parse Japanese natural language date/time into timezone-aware datetime.

    If `timezone` is provided (IANA name or tz string), use it as parsing timezone so
    phrases like '明日 10時' are interpreted in that zone.
    """
    settings = {"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": True}
    if timezone:
        settings["TIMEZONE"] = timezone
    else:
        settings["TIMEZONE"] = "UTC"

    dt = dateparser.parse(text, languages=["ja"], settings=settings)
    if dt is None:
        raise ValueError("日付を解析できませんでした。入力を確認してください。")
    # If parsed datetime is naive, attach local timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.tzlocal())
    return dt
