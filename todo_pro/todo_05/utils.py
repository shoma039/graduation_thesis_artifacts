from dateparser import parse
from datetime import datetime, date
from zoneinfo import ZoneInfo
from typing import Optional

def parse_natural_date(text: str, tz_name: str) -> Optional[date]:
    """日本語の自然言語日付をパースして、その日の date を返す（タイムゾーン考慮）。"""
    if not text or not text.strip():
        return None
    try:
        settings = {
            'PREFER_DATES_FROM': 'future',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'TIMEZONE': tz_name,
            'LANGUAGE': 'ja'
        }
        dt = parse(text, settings=settings)
        if dt is None:
            return None
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=ZoneInfo(tz_name))
        return dt.date()
    except Exception:
        return None
