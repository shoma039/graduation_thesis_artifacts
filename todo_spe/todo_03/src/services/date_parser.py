import dateparser
from datetime import datetime
from zoneinfo import ZoneInfo


def parse_natural_date(text: str, tz: str = "UTC") -> datetime:
    """Parse natural language date string into timezone-aware datetime."""
    settings = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "TIMEZONE": tz,
        "TO_TIMEZONE": tz,
    }
    dt = dateparser.parse(text, settings=settings, languages=["ja"])  # try Japanese
    if dt is None:
        raise ValueError("日付を解釈できませんでした。入力を確認してください。")
    # Ensure tzinfo exists
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz))
    return dt
