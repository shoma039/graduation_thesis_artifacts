from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from src.services.weather import get_daily_weather
from src.storage.store import Store


def select_candidate_dates(due_iso: str, location: Dict, max_candidates: int = 1) -> List[Dict]:
    """Select candidate dates within [today, due_date] based on lowest precipitation.

    location: {name, latitude, longitude, timezone}
    returns list of candidate dicts with date, precipitation_probability, temperature, reason
    """
    try:
        due_dt = datetime.fromisoformat(due_iso)
    except Exception:
        # fallback: treat as date
        due_dt = datetime.utcnow()
    today = datetime.now()
    start = today.date()
    end = due_dt.date()
    if end < start:
        end = start

    weather = get_daily_weather(location["latitude"], location["longitude"], start, end, timezone=location.get("timezone", "UTC"))

    # produce scored list
    scored = []
    for d, info in weather.items():
        p = info.get("precipitation_probability")
        t = info.get("temperature")
        score = (p if p is not None else 100)  # lower is better
        scored.append((d, score, p, t))

    scored.sort(key=lambda x: (x[1], -(x[3] or 0)))

    # check existing candidate conflicts
    store = Store()
    existing = set()
    for t in store.list_tasks():
        for c in t.get("candidate_dates", []):
            existing.add(c.get("date"))

    out = []
    for d, score, p, t in scored:
        if d in existing:
            continue
        out.append({
            "date": d,
            "precipitation_probability": p,
            "temperature": t,
            "reason": "降水確率が低いため",
        })
        if len(out) >= max_candidates:
            break

    # if none found, suggest next available dates after due_date
    if not out:
        alt_start = end + timedelta(days=1)
        alt_end = alt_start + timedelta(days=7)
        alt_weather = get_daily_weather(location["latitude"], location["longitude"], alt_start, alt_end, timezone=location.get("timezone", "UTC"))
        for d, info in alt_weather.items():
            out.append({"date": d, "precipitation_probability": info.get("precipitation_probability"), "temperature": info.get("temperature"), "reason": "候補日が期限内に見つからなかったため予備日"})
            if len(out) >= max_candidates:
                break

    return out
