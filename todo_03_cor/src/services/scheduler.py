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

    """def pick_candidate(self, latitude: float, longitude: float, timezone: str, due: date) -> Dict:
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
        return None"""
    
    def pick_candidate(self, latitude: float, longitude: float, timezone: str, due: date) -> Dict:
        today = date.today()
        start = today
        end = due
        
        # --- 1. API制限（今日から14日後）を計算 ---
        api_limit_date = today + timedelta(days=14)
        
        # 最初の天気取得が限界を超えないようにキャップする
        fetch_end = min(end, api_limit_date)
        
        # 期限内の天気を取得
        weather = fetch_daily_weather(latitude, longitude, start, fetch_end, timezone)
        
        # 降水確率順 -> 日付順 でソート
        sorted_days = sorted(weather, key=lambda x: (x.get("precipitation_probability") if x.get("precipitation_probability") is not None else 100, x.get("date")))
        
        # 既存の予約済み日程を取得
        data = self.storage.load_all()
        occupied = set()
        for t in data.get("tasks", []):
            for c in t.get("candidate_dates", []):
                occupied.add(c.get("date"))
        
        # 期限内で空きを探す
        for day in sorted_days:
            d = day.get("date")
            if isinstance(d, str):
                d = date.fromisoformat(d)
            
            # 日付比較（文字列型に合わせて比較）
            if d.isoformat() not in occupied:
                return {"date": d.isoformat(), "precipitation_probability": day.get("precipitation_probability"), "temperature": day.get("temperature"), "reason": "降水確率最小"}

        # --- 2. 期限内に空きがない場合 (fallback) ---
        # 期限の翌日から探索
        fallback_start = end + timedelta(days=1)
        
        # ここが修正点：検索終了日が「APIの限界」を超えないようにする
        fallback_end_raw = end + timedelta(days=14)
        fallback_end = min(fallback_end_raw, api_limit_date)

        weather2 = []
        # API予報可能な範囲内であれば天気を取得
        if fallback_start <= fallback_end:
            weather2 = fetch_daily_weather(latitude, longitude, fallback_start, fallback_end, timezone)
        
        sorted_fallback = sorted(weather2, key=lambda x: (x.get("precipitation_probability") if x.get("precipitation_probability") is not None else 100, x.get("date")))

        # 天気がわかっている範囲で空きを探す
        for day in sorted_fallback:
            d = day.get("date")
            if isinstance(d, str):
                d = date.fromisoformat(d)
                
            if d.isoformat() not in occupied:
                return {"date": d.isoformat(), "precipitation_probability": day.get("precipitation_probability"), "temperature": day.get("temperature"), "reason": "期限外の予備日(天気考慮)"}

        # 天気が取れない（未来すぎる）場合でも、とりあえず空いている日を探す
        check_date = fallback_start
        for _ in range(14):
            if check_date.isoformat() not in occupied:
                 return {"date": check_date.isoformat(), "precipitation_probability": None, "temperature": None, "reason": "期限外の予備日(天気不明)"}
            check_date += timedelta(days=1)

        return None
