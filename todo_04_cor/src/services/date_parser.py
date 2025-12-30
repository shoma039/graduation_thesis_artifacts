import dateparser
from datetime import datetime


def parse_japanese_date(text):
    # dateparser with languages=['ja'] to support Japanese expressions
    settings = {"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": False}
    dt = dateparser.parse(text, languages=["ja"], settings=settings)
    if not dt:
        return None
    # normalize to datetime (naive UTC for storage later)
    return dt
