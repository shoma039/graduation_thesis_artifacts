#!/usr/bin/env python
"""
シンプルな対話型Todo CLI
"""
import sqlite3
import requests
import sys
import datetime
from zoneinfo import ZoneInfo
import dateparser
from typing import Optional, Tuple, List

DB_PATH = "todo.db"

def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority INTEGER NOT NULL,
            location_name TEXT,
            lat REAL,
            lon REAL,
            timezone TEXT,
            deadline TEXT,
            candidate_date TEXT,
            candidate_precip REAL,
            candidate_temp_max REAL,
            done INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )
    conn.commit()

def geocode_city(q: str) -> Optional[Tuple[float,float,str]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": q, "format": "json", "limit": 1}
    headers = {"User-Agent": "todo-cli-app (example)"}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        item = data[0]
        return (float(item['lat']), float(item['lon']), item.get('display_name', q))
    except Exception as e:
        print(f"ジオコーディング中にエラー: {e}")
        return None

def get_timezone(lat: float, lon: float) -> Optional[str]:
    url = "https://api.open-meteo.com/v1/timezone"
    params = {"latitude": lat, "longitude": lon}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get('timezone')
    except Exception as e:
        print(f"タイムゾーン取得中にエラー: {e}")
        return None

def fetch_weather_daily(lat: float, lon: float, tz: str, start_date: datetime.date, end_date: datetime.date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "precipitation_probability_mean,temperature_2m_max,temperature_2m_min"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def parse_deadline(text: str, tz: str) -> Optional[datetime.date]:
    settings = {
        'PREFER_DATES_FROM': 'future',
        'TIMEZONE': tz,
        'RETURN_AS_TIMEZONE_AWARE': True,
    }
    dt = dateparser.parse(text, settings=settings, languages=['ja'])
    if not dt:
        return None
    # Convert to date in the given timezone
    try:
        # ensure tz-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(tz))
        local = dt.astimezone(ZoneInfo(tz))
        return local.date()
    except Exception:
        return dt.date()

def pick_candidate_date(conn: sqlite3.Connection, lat: float, lon: float, tz: str, deadline: datetime.date) -> Tuple[Optional[datetime.date], Optional[float], Optional[float]]:
    today = datetime.datetime.now(tz=ZoneInfo(tz)).date()
    if deadline < today:
        return (None, None, None)

    # Build date range and fetch weather. Open-Meteo supports a wide range; keep in one call.
    start = today
    end = deadline
    try:
        data = fetch_weather_daily(lat, lon, tz, start, end)
    except Exception as e:
        print(f"天気予報取得エラー: {e}")
        return (None, None, None)

    dates = data.get('daily', {}).get('time', [])
    precips = data.get('daily', {}).get('precipitation_probability_mean', [])
    temps_max = data.get('daily', {}).get('temperature_2m_max', [])

    # existing candidate dates to avoid
    cur = conn.cursor()
    cur.execute("SELECT candidate_date FROM tasks WHERE candidate_date IS NOT NULL")
    used = set(r[0] for r in cur.fetchall())

    candidates = []
    for d, p, t in zip(dates, precips, temps_max):
        candidates.append((d, p if p is not None else 100.0, t))

    # sort by precip asc then earlier date
    candidates.sort(key=lambda x: (x[1], x[0]))

    chosen = None
    for d_str, p, t in candidates:
        if d_str in used:
            continue
        chosen = (datetime.date.fromisoformat(d_str), p, t)
        break

    if chosen:
        return chosen

    # もし最適日がなければ、期限内で空いている最初の日を提案
    for d_str, p, t in candidates:
        if d_str not in used:
            return (datetime.date.fromisoformat(d_str), p, t)

    # それでもなければ、期限後の最初の空き日を探す（期限+1日から30日以内）
    for extra in range(1, 31):
        day = end + datetime.timedelta(days=extra)
        try:
            data2 = fetch_weather_daily(lat, lon, tz, day, day)
            dates2 = data2.get('daily', {}).get('time', [])
            if not dates2:
                continue
            p = data2.get('daily', {}).get('precipitation_probability_mean', [None])[0]
            t = data2.get('daily', {}).get('temperature_2m_max', [None])[0]
            day_str = day.isoformat()
            if day_str in used:
                continue
            return (day, p if p is not None else None, t)
        except Exception:
            continue

    return (None, None, None)

def add_task(conn: sqlite3.Connection):
    title = input("タイトル: ").strip()
    if not title:
        print("タイトルは必須です。")
        return

    pr = input("優先度(1=高,2=中,3=低): ").strip()
    if pr not in ('1','2','3'):
        print("優先度は1,2,3のいずれかを指定してください。")
        return
    priority = int(pr)

    loc = input("場所（都市名）: ").strip()
    if not loc:
        print("場所は必須です。")
        return

    geo = geocode_city(loc)
    if not geo:
        print("場所が見つかりませんでした。別の名称を試してください。")
        return
    lat, lon, display_name = geo

    tz = get_timezone(lat, lon)
    if not tz:
        print("タイムゾーンが取得できませんでした。処理を中止します。")
        return

    dl_text = input("期限（日付、例: '明日'、'2025-12-31'、'来週の月曜'）: ").strip()
    dl = parse_deadline(dl_text, tz)
    if not dl:
        print("期限の解析に失敗しました。もう一度入力してください。")
        return

    cand_date, cand_precip, cand_temp = pick_candidate_date(conn, lat, lon, tz, dl)

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, priority, location_name, lat, lon, timezone, deadline, candidate_date, candidate_precip, candidate_temp_max, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (title, priority, display_name, lat, lon, tz, dl.isoformat(), cand_date.isoformat() if cand_date else None, cand_precip, cand_temp, datetime.datetime.now(datetime.timezone.utc).isoformat())
    )
    conn.commit()
    print(f"タスクを登録しました。候補日: {cand_date} (降水確率: {cand_precip}%, 最高気温: {cand_temp}°C)" if cand_date else "候補日は自動選定できませんでした。")

def list_tasks(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT id, title, priority, deadline, candidate_date, location_name FROM tasks ORDER BY deadline ASC")
    rows = cur.fetchall()
    if not rows:
        print("タスクがありません。")
        return
    print("ID  優先  期限        候補日      場所  タイトル")
    for r in rows:
        print(f"{r[0]:<3}  {r[2]}     {r[3] or '-'}  {r[4] or '-'}  {r[5]}  {r[1]}")

def show_task(conn: sqlite3.Connection):
    tid = input("表示するタスクID: ").strip()
    if not tid.isdigit():
        print("IDは数値で指定してください。")
        return
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (int(tid),))
    row = cur.fetchone()
    if not row:
        print("指定のIDは見つかりません。")
        return
    keys = [d[0] for d in cur.description]
    d = dict(zip(keys, row))
    print("--- タスク詳細 ---")
    print(f"ID: {d['id']}")
    print(f"タイトル: {d['title']}")
    print(f"優先度: {d['priority']}")
    print(f"場所: {d['location_name']} (lat={d['lat']}, lon={d['lon']})")
    print(f"タイムゾーン: {d['timezone']}")
    print(f"期限: {d['deadline']}")
    print(f"候補日: {d['candidate_date']} (降水確率: {d['candidate_precip']}, 最高気温: {d['candidate_temp_max']})")
    print(f"作成日時(UTC): {d['created_at']}")

def delete_task(conn: sqlite3.Connection):
    tid = input("削除するタスクID: ").strip()
    if not tid.isdigit():
        print("IDは数値で指定してください。")
        return
    cur = conn.cursor()
    cur.execute("SELECT title FROM tasks WHERE id = ?", (int(tid),))
    row = cur.fetchone()
    if not row:
        print("指定のIDは見つかりません。")
        return
    confirm = input(f"タスク '{row[0]}' を本当に削除しますか？(y/n): ").strip().lower()
    if confirm != 'y':
        print("削除をキャンセルしました。")
        return
    cur.execute("DELETE FROM tasks WHERE id = ?", (int(tid),))
    conn.commit()
    print("削除しました。")

def update_task(conn: sqlite3.Connection):
    tid = input("更新するタスクID: ").strip()
    if not tid.isdigit():
        print("IDは数値で指定してください。")
        return
    cur = conn.cursor()
    cur.execute("SELECT id, title, priority, location_name, lat, lon, timezone, deadline, candidate_date FROM tasks WHERE id = ?", (int(tid),))
    row = cur.fetchone()
    if not row:
        print("指定のIDは見つかりません。")
        return
    print("更新したい項目を入力（空欄で変更なし）")
    title = input(f"タイトル [{row[1]}]: ").strip() or row[1]
    pr = input(f"優先度(1-3) [{row[2]}]: ").strip() or str(row[2])
    if pr not in ('1','2','3'):
        print("優先度は1,2,3のいずれかを指定してください。更新中止。")
        return
    # 更新可能項目: タイトル, 優先度
    cur.execute("UPDATE tasks SET title = ?, priority = ? WHERE id = ?", (title, int(pr), int(tid)))
    conn.commit()
    # 完了にする場合は削除する
    done = input("完了にしますか？(y/n): ").strip().lower()
    if done == 'y':
        cur.execute("DELETE FROM tasks WHERE id = ?", (int(tid),))
        conn.commit()
        print("タスクは完了として削除されました。")
    else:
        print("更新しました。")

def calendar_view(conn: sqlite3.Connection):
    ym = input("表示する年月を入力（YYYY-MM、未入力で今月）: ").strip()
    if not ym:
        dt = datetime.date.today()
    else:
        try:
            dt = datetime.datetime.strptime(ym + "-01", "%Y-%m-%d").date()
        except Exception:
            print("年月の形式が不正です。例: 2025-12")
            return
    first = dt.replace(day=1)
    last_day = (first.replace(month=first.month % 12 + 1, day=1) - datetime.timedelta(days=1)).day

    cur = conn.cursor()
    cur.execute("SELECT id, title, deadline, candidate_date FROM tasks WHERE deadline BETWEEN ? AND ? ORDER BY deadline ASC",
                (first.isoformat(), first.replace(day=last_day).isoformat()))
    rows = cur.fetchall()
    if not rows:
        print("この月のタスクはありません。")
        return
    print(f"{first.year}年{first.month}月 のタスク（期限順）")
    for r in rows:
        print(f"{r[2]}: ID{r[0]} {r[1]} (候補日: {r[3] or '-'})")

def main_loop(conn: sqlite3.Connection):
    actions = {
        '1': ('登録', add_task),
        '2': ('一覧', list_tasks),
        '3': ('詳細表示', show_task),
        '4': ('更新', update_task),
        '5': ('削除', delete_task),
        '6': ('カレンダー表示', calendar_view),
        'q': ('終了', None)
    }
    while True:
        print('\n--- Todo CLI ---')
        for k, v in actions.items():
            print(f"{k}: {v[0]}")
        cmd = input("選択: ").strip()
        if cmd == 'q':
            print("終了します。")
            break
        action = actions.get(cmd)
        if not action:
            print("無効な選択です。")
            continue
        func = action[1]
        try:
            func(conn)
        except Exception as e:
            print(f"操作中にエラーが発生しました: {e}")

if __name__ == '__main__':
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    main_loop(conn)
    conn.close()
