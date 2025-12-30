#!/usr/bin/env python3
"""
簡易Todo CLIアプリ

機能:
- 登録 (自然言語日付入力をサポート: 日本語例「明日」「来週の月曜」)
- 一覧
- 詳細表示
- 更新 (完了にすると削除)
- 削除
- カレンダー表示 (月選択)

外部API:
- ジオコーディング: Nominatim (OpenStreetMap)
- タイムゾーン/天気: Open-Meteo (APIキー不要)

依存: requests, dateparser, tzdata

保存: `tasks.json` に永続化

出力は日本語。
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

import requests
import dateparser
from zoneinfo import ZoneInfo

STORAGE_FILE = "tasks.json"
USER_AGENT = "todo-cli-app/1.0 (mailto:example@example.com)"


@dataclass
class Task:
    id: int
    title: str
    done: bool
    priority: str  # low, medium, high
    location_name: str
    latitude: float
    longitude: float
    timezone: str
    deadline: str  # ISO date YYYY-MM-DD
    candidate_date: Optional[str]
    created_at: str
    updated_at: str


def load_tasks() -> List[Task]:
    if not os.path.exists(STORAGE_FILE):
        return []
    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task(**t) for t in data]


def save_tasks(tasks: List[Task]) -> None:
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in tasks], f, ensure_ascii=False, indent=2)


def next_id(tasks: List[Task]) -> int:
    return max((t.id for t in tasks), default=0) + 1


def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1, "accept-language": "ja"}
    #'TodoCLI/1.0 (satosho311039@gmail.com)'}を記載
    headers = {"User-Agent":'TodoCLI/1.0 (satosho311039@gmail.com)'}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"[エラー] ジオコーディングに失敗しました: HTTP {resp.status_code}")
        return None
    arr = resp.json()
    if not arr:
        print("[エラー] 指定された都市が見つかりませんでした。")
        return None
    return arr[0]


def get_timezone(lat: float, lon: float) -> Optional[str]:
    #URLを修正
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon}
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        print(f"[エラー] タイムゾーン取得に失敗しました: HTTP {resp.status_code}")
        return None
    data = resp.json()
    return data.get("timezone")


def parse_date_nl(text: str, tzname: str) -> Optional[date]:
    try:
        base = datetime.now(ZoneInfo(tzname))
    except Exception:
        base = datetime.now()
    settings = {"RELATIVE_BASE": base, "PREFER_DATES_FROM": "future"}
    dt = dateparser.parse(text, languages=["ja"], settings=settings)
    if not dt:
        return None
    # Ensure in local timezone
    if dt.tzinfo is None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(tzname))
        except Exception:
            pass
    return dt.date()


def fetch_weather_daily(lat: float, lon: float, tzname: str, start_date: date, end_date: date) -> Optional[Dict[str, Dict[str, Any]]]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(["precipitation_probability_max", "temperature_2m_max", "temperature_2m_min"]),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": tzname,
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        print(f"[エラー] 天気予報取得に失敗しました: HTTP {resp.status_code}")
        return None
    data = resp.json()
    daily = data.get("daily")
    if not daily:
        print("[エラー] 天気データが取得できませんでした。")
        return None
    dates = daily.get("time", [])
    pps = daily.get("precipitation_probability_max", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    out = {}
    for i, d in enumerate(dates):
        out[d] = {
            "precipitation_probability_max": pps[i] if i < len(pps) else None,
            "temperature_max": tmax[i] if i < len(tmax) else None,
            "temperature_min": tmin[i] if i < len(tmin) else None,
        }
    return out


def choose_candidate_date(tasks: List[Task], lat: float, lon: float, tzname: str, start_date: date, end_date: date) -> Optional[Dict[str, Any]]:
    weather = fetch_weather_daily(lat, lon, tzname, start_date, end_date)
    if weather is None:
        return None
    # 集合: 既に確保されている候補日
    reserved = {t.candidate_date for t in tasks if t.candidate_date}

    # 期限内で降水確率の低い順に並べて空きがあれば採用
    candidates = []
    for d_iso, info in weather.items():
        try:
            p = info.get("precipitation_probability_max")
            candidates.append((d_iso, p or 999, info))
        except Exception:
            continue
    candidates.sort(key=lambda x: (x[1], x[0]))
    for d_iso, p, info in candidates:
        if d_iso not in reserved:
            return {"date": d_iso, "precipitation": p, "temp_min": info.get("temperature_min"), "temp_max": info.get("temperature_max")}

    # もし期限内で空きがない場合、期限内で最も降水確率が低い "予備" 日を提案する（ただし日付は予約済みでも可）
    if candidates:
        d_iso, p, info = candidates[0]
        return {"date": d_iso, "precipitation": p, "temp_min": info.get("temperature_min"), "temp_max": info.get("temperature_max"), "note": "期限内だが候補日が重複していたため予備として提案"}

    return None


def register_task(tasks: List[Task]) -> None:
    print("--- タスク登録 ---")
    title = input("タイトル: ").strip()
    if not title:
        print("[エラー] タイトルは必須です。")
        return
    priority = input("優先度 (low/medium/high) [medium]: ").strip().lower() or "medium"
    if priority not in ("low", "medium", "high"):
        print("[エラー] 優先度は low, medium, high のいずれかです。")
        return
    loc = input("場所（都市名）例: 東京: ").strip()
    if not loc:
        print("[エラー] 場所は必須です。")
        return
    geo = geocode_city(loc)
    if not geo:
        return
    lat = float(geo["lat"])  # type: ignore
    lon = float(geo["lon"])  # type: ignore
    tzname = get_timezone(lat, lon)
    if not tzname:
        return
    ddl_input = input("期限（日付・日本語の自然言語可）例: '明日', '来週の月曜', '2025-12-20': ").strip()
    ddl_date = parse_date_nl(ddl_input, tzname) if ddl_input else None
    if not ddl_date:
        print("[エラー] 期限のパースに失敗しました。例: '明日' または '2025-12-20' の形式で再度お試しください。")
        return

    today = datetime.now(ZoneInfo(tzname)).date()
    if ddl_date < today:
        print("[エラー] 期限は今日以降の日付を指定してください。")
        return

    candidate = choose_candidate_date(tasks, lat, lon, tzname, today, ddl_date)

    tid = next_id(tasks)
    now_iso = datetime.utcnow().isoformat() + "Z"
    t = Task(
        id=tid,
        title=title,
        done=False,
        priority=priority,
        location_name=geo.get("display_name", loc),
        latitude=lat,
        longitude=lon,
        timezone=tzname,
        deadline=ddl_date.isoformat(),
        candidate_date=candidate.get("date") if candidate else None,
        created_at=now_iso,
        updated_at=now_iso,
    )
    tasks.append(t)
    save_tasks(tasks)
    print(f"タスクを登録しました (ID: {t.id})")
    if candidate:
        note = candidate.get("note")
        print("候補日:", candidate["date"], f"降水確率: {candidate['precipitation']}%", f"気温(最小〜最大): {candidate.get('temp_min')}〜{candidate.get('temp_max')}°C", "注意:" , note if note else "")


def list_tasks(tasks: List[Task]) -> None:
    if not tasks:
        print("タスクはありません。")
        return
    print("--- タスク一覧 ---")
    for t in sorted(tasks, key=lambda x: x.id):
        cand = t.candidate_date or "(未設定)"
        print(f"ID:{t.id} | {t.title} | 優先度:{t.priority} | 期限:{t.deadline} | 候補日:{cand}")


def show_detail(tasks: List[Task]) -> None:
    tid_s = input("表示するタスクのID: ").strip()
    if not tid_s.isdigit():
        print("[エラー] 数字のIDを入力してください。")
        return
    tid = int(tid_s)
    t = next((x for x in tasks if x.id == tid), None)
    if not t:
        print("[エラー] タスクが見つかりません。")
        return
    print("--- タスク詳細 ---")
    print(f"ID: {t.id}")
    print(f"タイトル: {t.title}")
    print(f"優先度: {t.priority}")
    print(f"場所: {t.location_name} ({t.latitude}, {t.longitude}) タイムゾーン: {t.timezone}")
    print(f"期限: {t.deadline}")
    print(f"候補日: {t.candidate_date or '(未設定)'}")
    print(f"作成: {t.created_at} 更新: {t.updated_at}")


def update_task(tasks: List[Task]) -> None:
    tid_s = input("更新するタスクのID: ").strip()
    if not tid_s.isdigit():
        print("[エラー] 数字のIDを入力してください。")
        return
    tid = int(tid_s)
    idx = next((i for i, x in enumerate(tasks) if x.id == tid), None)
    if idx is None:
        print("[エラー] タスクが見つかりません。")
        return
    t = tasks[idx]
    print(f"現在のタイトル: {t.title}")
    new_title = input("新しいタイトル（空欄で変更しない）: ").strip()
    if new_title:
        t.title = new_title
    new_pri = input(f"優先度 (low/medium/high) [{t.priority}]: ").strip().lower()
    if new_pri:
        if new_pri in ("low", "medium", "high"):
            t.priority = new_pri
        else:
            print("[警告] 優先度は変更されませんでした。")

    mark_done = input("完了にしますか？ (y/n): ").strip().lower()
    if mark_done == "y":
        # 要求仕様: タスクを更新して完了となったらそのタスクは削除する
        del tasks[idx]
        save_tasks(tasks)
        print("タスクは完了扱いで削除されました。")
        return

    # 期限変更
    new_deadline = input(f"期限（現在:{t.deadline}）日本語可: ").strip()
    if new_deadline:
        new_dead = parse_date_nl(new_deadline, t.timezone)
        if not new_dead:
            print("[警告] 期限のパースに失敗しました。期限は変更されませんでした。")
        else:
            t.deadline = new_dead.isoformat()
            # 候補日を再計算
            today = datetime.now(ZoneInfo(t.timezone)).date()
            candidate = choose_candidate_date([x for x in tasks if x.id != t.id], t.latitude, t.longitude, t.timezone, today, new_dead)
            t.candidate_date = candidate.get("date") if candidate else None
            if candidate:
                print("新しい候補日:", candidate["date"], f"降水確率: {candidate['precipitation']}%")

    t.updated_at = datetime.utcnow().isoformat() + "Z"
    tasks[idx] = t
    save_tasks(tasks)
    print("タスクを更新しました。")


def delete_task(tasks: List[Task]) -> None:
    tid_s = input("削除するタスクのID: ").strip()
    if not tid_s.isdigit():
        print("[エラー] 数字のIDを入力してください。")
        return
    tid = int(tid_s)
    idx = next((i for i, x in enumerate(tasks) if x.id == tid), None)
    if idx is None:
        print("[エラー] タスクが見つかりません。")
        return
    confirm = input("本当に削除しますか？ (y/n): ").strip().lower()
    if confirm != "y":
        print("削除をキャンセルしました。")
        return
    del tasks[idx]
    save_tasks(tasks)
    print("タスクを削除しました。")


def show_calendar(tasks: List[Task]) -> None:
    print("--- カレンダー表示 ---")
    mm = input("表示する年月を入力 (YYYY-MM) または空欄で今月: ").strip()
    if not mm:
        today = date.today()
        year = today.year
        month = today.month
    else:
        try:
            parts = mm.split("-")
            year = int(parts[0])
            month = int(parts[1])
        except Exception:
            print("[エラー] YYYY-MM の形式で入力してください。")
            return
    first = date(year, month, 1)
    # 月末計算
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    print(f"{year}年{month}月 のタスク (候補日ベース)")
    # その月の候補日を日付順で表示
    cal_tasks = [t for t in tasks if t.candidate_date]
    by_day: Dict[str, List[Task]] = {}
    for t in cal_tasks:
        try:
            d = datetime.fromisoformat(t.candidate_date).date() if t.candidate_date else None
        except Exception:
            d = None
        if d and first <= d <= last:
            by_day.setdefault(d.isoformat(), []).append(t)

    d = first
    while d <= last:
        day_tasks = by_day.get(d.isoformat(), [])
        line = f"{d.isoformat()}: "
        if day_tasks:
            summaries = [f"(ID{tt.id}){tt.title}[優:{tt.priority}]@{tt.location_name.split(',')[0]}" for tt in day_tasks]
            line += ", ".join(summaries)
        else:
            line += "-"
        print(line)
        d += timedelta(days=1)


def main_loop():
    tasks = load_tasks()
    while True:
        print("\n--- Todo CLI ---")
        print("1) 登録 2) 一覧 3) 詳細 4) 更新 5) 削除 6) カレンダー 7) 終了")
        choice = input("選択: ").strip()
        if choice == "1":
            register_task(tasks)
        elif choice == "2":
            list_tasks(tasks)
        elif choice == "3":
            show_detail(tasks)
        elif choice == "4":
            update_task(tasks)
            tasks = load_tasks()
        elif choice == "5":
            delete_task(tasks)
            tasks = load_tasks()
        elif choice == "6":
            show_calendar(tasks)
        elif choice == "7":
            print("終了します。")
            break
        else:
            print("不明な選択です。番号を入力してください。")


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n終了します。")
