from __future__ import annotations

from datetime import datetime
from typing import Optional

import dateparser
from datetime import timedelta
from zoneinfo import ZoneInfo
import re


def parse_date(text: str, timezone: Optional[str] = None, prefer_future: bool = True) -> Optional[datetime]:
    """Parse a Japanese (or general) natural-language date/time string into a timezone-aware datetime.

    Args:
        text: input natural-language string (e.g. '明日', '来週の月曜', '2026/01/05 14:00')
        timezone: IANA timezone string (e.g. 'Asia/Tokyo'). If provided, used for interpretation.
        prefer_future: whether to prefer future dates when ambiguous.

    Returns:
        A timezone-aware `datetime` or `None` if parsing failed.
    """
    if not text or not text.strip():
        return None
    # Basic normalization for common Japanese weekday abbreviations
    text = text.strip()
    replacements = {
        "月曜": "月曜日",
        "火曜": "火曜日",
        "水曜": "水曜日",
        "木曜": "木曜日",
        "金曜": "金曜日",
        "土曜": "土曜日",
        "日曜": "日曜日",
    }
    for k, v in replacements.items():
        if k in text:
            text = text.replace(k, v)

    settings = {
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future" if prefer_future else "current_period",
    }

    if timezone:
        settings["TIMEZONE"] = timezone

    # dateparser supports a `languages` argument; prefer Japanese for this project
    try:
        dt = dateparser.parse(text, settings=settings, languages=["ja"])  # type: ignore[arg-type]
    except Exception:
        dt = None

    # Fallback: try without forcing language (sometimes expressions parse better)
    if dt is None:
        try:
            dt = dateparser.parse(text, settings=settings)
        except Exception:
            dt = None

    # Additional heuristic fallbacks for common Japanese patterns
    if dt is None:
        today = datetime.now()

        # 来週の月曜日 等
        m = re.search(r"来週の?(月曜日|火曜日|水曜日|木曜日|金曜日|土曜日|日曜日)", text)
        if m:
            name = m.group(1)
            mapping = {
                "月曜日": 0,
                "火曜日": 1,
                "水曜日": 2,
                "木曜日": 3,
                "金曜日": 4,
                "土曜日": 5,
                "日曜日": 6,
            }
            target = mapping.get(name)
            if target is not None:
                days_ahead = (target - today.weekday() + 7) % 7
                if days_ahead == 0:
                    days_ahead = 7
                days = days_ahead + 7
                d = today + timedelta(days=days)
                # set a default time of 09:00
                dt = datetime(d.year, d.month, d.day, 9, 0)

        # 来月第2金曜 のような表現
        if dt is None:
            m2 = re.search(r"来月第(\d+)\s*(日|月|火|水|木|金|土)曜", text)
            if m2:
                try:
                    nth = int(m2.group(1))
                    w = m2.group(2)
                    mapping2 = {"日": 6, "月": 0, "火": 1, "水": 2, "木": 3, "金": 4, "土": 5}
                    target = mapping2.get(w)
                    if target is not None:
                        # compute next month
                        y = today.year + (1 if today.month == 12 else 0)
                        mth = 1 if today.month == 12 else today.month + 1
                        first = datetime(y, mth, 1)
                        # find first target weekday in month
                        offset = (target - first.weekday() + 7) % 7
                        day = 1 + offset + (nth - 1) * 7
                        try:
                            dt = datetime(y, mth, day, 9, 0)
                        except Exception:
                            dt = None
                except Exception:
                    dt = None

    # If we constructed a naive datetime and a timezone was requested, make it timezone-aware
    if dt is not None and timezone and dt.tzinfo is None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(timezone))
        except Exception:
            # best-effort: leave naive if zoneinfo not available
            pass

    return dt


def to_iso(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    # Ensure isoformat includes offset
    return dt.isoformat()
