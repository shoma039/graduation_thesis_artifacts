from calendar import monthcalendar, month_name
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional


def _parse_date_iso(dt_str: str, tz: Optional[str] = None) -> Optional[datetime]:
    if not dt_str:
        return None
    try:
        # datetime.fromisoformat supports offsets
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None and tz:
            dt = dt.replace(tzinfo=ZoneInfo(tz))
        return dt
    except Exception:
        return None


def render_month(year: int, month: int, tasks: List[Dict], timezone: Optional[str] = None) -> str:
    """Render a simple text calendar for the month, annotating days with task titles."""
    cal = monthcalendar(year, month)
    title = f"{year}年 {month}月"
    lines = [title]
    lines.append("Mo Tu We Th Fr Sa Su")

    # build mapping day -> list of task titles
    day_map = {}
    for t in tasks:
        due = t.get("due_date")
        dt = _parse_date_iso(due, tz=(t.get("location", {}).get("timezone") or timezone))
        if dt is None:
            continue
        d = dt.date()
        if d.year == year and d.month == month:
            day_map.setdefault(d.day, []).append(t.get("title", "(無題)"))

    for week in cal:
        week_str = []
        for d in week:
            if d == 0:
                week_str.append("  ")
            else:
                if d in day_map:
                    # mark with * if tasks
                    week_str.append(f"{d:2d}*")
                else:
                    week_str.append(f"{d:2d}")
        lines.append(" ".join(week_str))

    # append task list with dates
    lines.append("")
    lines.append("タスク一覧:")
    for day in sorted(day_map.keys()):
        titles = ", ".join(day_map[day])
        lines.append(f"{year}-{month:02d}-{day:02d}: {titles}")

    return "\n".join(lines)
