from datetime import date, timedelta, datetime
from typing import List, Dict

from .weather import fetch_daily_weather
from .storage import Storage


def date_range(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


class Scheduler:
    def __init__(self, storage: Storage):
        self.storage = storage

    def pick_candidate(self, latitude: float, longitude: float, timezone: str, due: date) -> Dict:
        today = date.today()
        start = today
        end = due
        weather = fetch_daily_weather(latitude, longitude, start, end, timezone)
        # sort by precipitation then date
        sorted_days = sorted(weather, key=lambda x: (x.get("precipitation_probability") if x.get("precipitation_probability") is not None else 100, x.get("date")))
        # get occupied candidate dates
        data = self.storage.load_all()
        occupied = set()
        for t in data.get("tasks", []):
            for c in t.get("candidate_dates", []):
                occupied.add(c.get("date"))
        for day in sorted_days:
            d = day.get("date")
            if d not in occupied:
                return {"date": d, "precipitation_probability": day.get("precipitation_probability"), "temperature": day.get("temperature"), "reason": "降水確率最小"}
        # fallback: search next 7 days after due
        fallback_start = end + timedelta(days=1)
        fallback_end = end + timedelta(days=14)
        weather2 = fetch_daily_weather(latitude, longitude, fallback_start, fallback_end, timezone)
        for day in weather2:
            d = day.get("date")
            if d not in occupied:
                return {"date": d, "precipitation_probability": day.get("precipitation_probability"), "temperature": day.get("temperature"), "reason": "期限外の予備日"}
        return None
