#!/usr/bin/env python3
"""
対話型Todo CLI

依存: requests, dateparser, pytz

外部API: Open-Meteo (ジオコーディング・天気) — APIキー不要
"""
import json
import os
import sys
import requests
from datetime import datetime, date, timedelta
import dateparser
import pytz
from zoneinfo import ZoneInfo

DATA_FILE = "tasks.json"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

PRIORITIES = {"1": "低", "2": "中", "3": "高"}


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def next_id(tasks):
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def geocode_city(city):
    params = {"name": city, "count": 1, "language": "ja"}
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data.get("results"):
        raise ValueError("都市が見つかりませんでした: {}".format(city))
    res = data["results"][0]
    return {
        "name": res.get("name"),
        "country": res.get("country"),
        "latitude": res.get("latitude"),
        "longitude": res.get("longitude"),
        "timezone": res.get("timezone") or res.get("timezone_name")
    }


def fetch_weather(lat, lon, tz, start_date, end_date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_probability_mean,temperature_2m_max,temperature_2m_min",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "timezone": tz
    }
    r = requests.get(WEATHER_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    pp = daily.get("precipitation_probability_mean", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    out = {}
    for i, d in enumerate(dates):
        out[d] = {
            "precip": pp[i] if i < len(pp) else None,
            "tmax": tmax[i] if i < len(tmax) else None,
            "tmin": tmin[i] if i < len(tmin) else None,
        }
    return out


def parse_date(text, tzname):
    settings = {
        "PREFER_DATES_FROM": "future",
        "TIMEZONE": tzname,
        "RETURN_AS_TIMEZONE_AWARE": True,
        "LANGUAGE": "ja",
    }
    dt = dateparser.parse(text, languages=["ja"], settings=settings)
    if dt is None:
        raise ValueError("日付の解析に失敗しました: {}".format(text))
    return dt


def date_range(start_date, end_date):
    d = start_date
    while d <= end_date:
        yield d
        d += timedelta(days=1)


def assign_candidate_day(task, tasks):
    # 他タスクの候補日を収集
    used_dates = set()
    for t in tasks:
        if t.get("candidate_date"):
            used_dates.add(t["candidate_date"])

    # 期限内の日を列挙
    tz = task["location"]["timezone"]
    due_dt = datetime.fromisoformat(task["due"]) if "T" in task["due"] else datetime.fromisoformat(task["due"] + "T00:00:00")
    today = datetime.now(ZoneInfo(tz)).date()
    end_date = due_dt.date()
    if end_date < today:
        return None, "期限が過ぎています"

    weather = fetch_weather(task["location"]["latitude"], task["location"]["longitude"], tz, today, end_date)

    # まず降水確率<=30%で空いている日を探す
    candidates = []
    for single in date_range(today, end_date):
        key = single.isoformat()
        w = weather.get(key)
        if not w:
            continue
        precip = w.get("precip")
        if key in used_dates:
            continue
        candidates.append((single, precip or 100, w))

    if not candidates:
        # 候補がない場合は空いている日を提案（降水情報が無いかすべて重複）
        for single in date_range(today, end_date):
            key = single.isoformat()
            if key in used_dates:
                continue
            return key, "候補日（天気データなしまたは空き日）"

    # 降水確率でソート
    candidates.sort(key=lambda x: (x[1], - (x[2].get("tmax") or 0)))
    # 良好閾値
    good = [c for c in candidates if c[1] <= 30]
    if good:
        chosen = good[0]
        return chosen[0].isoformat(), f"降水確率{chosen[1]}%、予想最高{chosen[2].get('tmax')}℃"

    # 良い日がない場合は最小降水確率の日を選ぶ（ただし衝突回避済み）
    chosen = candidates[0]
    return chosen[0].isoformat(), f"候補（降水確率{chosen[1]}%、予想最高{chosen[2].get('tmax')}℃）"


def cmd_add(tasks):
    try:
        title = input("タイトル: ").strip()
        if not title:
            print("エラー: タイトルは必須です")
            return
        pri = input("優先度（1=低,2=中,3=高）: ").strip()
        if pri not in PRIORITIES:
            print("エラー: 優先度は1/2/3を指定してください")
            return
        locname = input("場所（都市名）: ").strip()
        loc = geocode_city(locname)
        due_text = input("期限（日付、例: 明日、2025-12-31、来週の月曜）: ").strip()
        parsed = parse_date(due_text, loc["timezone"])  # aware datetime
        # store ISO with timezone
        due_iso = parsed.isoformat()

        task = {
            "id": next_id(tasks),
            "title": title,
            "done": False,
            "priority": pri,
            "location": loc,
            "due": due_iso,
            "candidate_date": None,
        }

        # 候補日を割り当てる
        cand, note = assign_candidate_day(task, tasks)
        if cand:
            task["candidate_date"] = cand
            print(f"候補日を割り当てました: {cand} ({note})")
        else:
            print(f"候補日の割当に問題: {note}")

        tasks.append(task)
        save_tasks(tasks)
        print(f"タスクを登録しました (ID={task['id']})")
    except Exception as e:
        print("エラー:", e)


def cmd_list(tasks):
    if not tasks:
        print("タスクはありません")
        return
    tasks_sorted = sorted(tasks, key=lambda t: t.get("candidate_date") or t.get("due"))
    for t in tasks_sorted:
        cand = t.get("candidate_date") or "(未設定)"
        print(f"[{t['id']}] {t['title']} 期限:{t['due'][:10]} 候補:{cand} 優先:{PRIORITIES.get(t['priority'])}")


def cmd_show(tasks, arg):
    try:
        idn = int(arg)
    except:
        print("エラー: 正しいIDを指定してください")
        return
    t = next((x for x in tasks if x["id"] == idn), None)
    if not t:
        print("該当するタスクが見つかりません")
        return
    print(json.dumps(t, ensure_ascii=False, indent=2))


def cmd_delete(tasks, arg):
    try:
        idn = int(arg)
    except:
        print("エラー: 正しいIDを指定してください")
        return
    i = next((idx for idx, x in enumerate(tasks) if x["id"] == idn), None)
    if i is None:
        print("該当するタスクが見つかりません")
        return
    tasks.pop(i)
    save_tasks(tasks)
    print("削除しました")


def cmd_update(tasks, arg):
    try:
        idn = int(arg)
    except:
        print("エラー: 正しいIDを指定してください")
        return
    t = next((x for x in tasks if x["id"] == idn), None)
    if not t:
        print("該当するタスクが見つかりません")
        return
    print(f"現在: {t['title']} 優先:{PRIORITIES.get(t['priority'])} 期限:{t['due']}")
    new_title = input("新タイトル（空欄で変更なし）: ").strip()
    if new_title:
        t["title"] = new_title
    new_pri = input("優先度（1/2/3  空欄で変更なし）: ").strip()
    if new_pri in PRIORITIES:
        t["priority"] = new_pri
    done = input("完了にする？ (y/n): ").strip().lower()
    if done == "y":
        # 完了なら削除
        tasks[:] = [x for x in tasks if x["id"] != idn]
        save_tasks(tasks)
        print("完了としてタスクを削除しました")
        return

    # 期限を編集する場合
    change_due = input("期限を変更しますか？ (y/n): ").strip().lower()
    if change_due == "y":
        try:
            loc = t["location"]
            due_text = input("新しい期限（日付）: ").strip()
            parsed = parse_date(due_text, loc["timezone"])
            t["due"] = parsed.isoformat()
        except Exception as e:
            print("期限の更新に失敗しました:", e)

    # 候補日を再割当
    cand, note = assign_candidate_day(t, [x for x in tasks if x["id"] != idn])
    if cand:
        t["candidate_date"] = cand
        print(f"新しい候補日: {cand} ({note})")
    save_tasks(tasks)
    print("更新しました")


def cmd_calendar(tasks, arg=None):
    today = datetime.now().date()
    if arg:
        try:
            y, m = arg.split("-")
            y = int(y); m = int(m)
            first = date(y, m, 1)
        except:
            print("エラー: 月の形式は YYYY-MM です")
            return
    else:
        first = date(today.year, today.month, 1)
    # 最終日
    if first.month == 12:
        last = date(first.year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(first.year, first.month + 1, 1) - timedelta(days=1)

    # 集約
    entries = []
    for t in tasks:
        d = t.get("candidate_date") or t.get("due")[:10]
        try:
            dd = date.fromisoformat(d)
        except:
            continue
        if first <= dd <= last:
            entries.append((dd, t))

    entries.sort(key=lambda x: x[0])
    if not entries:
        print("この月のタスクはありません")
        return
    for dd, t in entries:
        print(f"{dd.isoformat()} - [{t['id']}] {t['title']} 優先:{PRIORITIES.get(t['priority'])} 候補:{t.get('candidate_date')}")


def repl():
    tasks = load_tasks()
    print("Todo CLI（日本語）。'help' でコマンド一覧。")
    while True:
        try:
            cmd = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("終了します")
            return
        if not cmd:
            continue
        parts = cmd.split()
        c = parts[0]
        if c == "help":
            print("コマンド: add, list, show <id>, update <id>, delete <id>, calendar [YYYY-MM], help, quit")
        elif c == "add":
            cmd_add(tasks)
        elif c == "list":
            cmd_list(tasks)
        elif c == "show":
            if len(parts) < 2:
                print("IDを指定してください")
            else:
                cmd_show(tasks, parts[1])
        elif c == "delete":
            if len(parts) < 2:
                print("IDを指定してください")
            else:
                cmd_delete(tasks, parts[1])
        elif c == "update":
            if len(parts) < 2:
                print("IDを指定してください")
            else:
                cmd_update(tasks, parts[1])
        elif c == "calendar":
            arg = parts[1] if len(parts) > 1 else None
            cmd_calendar(tasks, arg)
        elif c in ("quit", "exit"):
            print("終了します")
            return
        else:
            print("不明なコマンド。'help' を参照してください。")


if __name__ == "__main__":
    repl()
