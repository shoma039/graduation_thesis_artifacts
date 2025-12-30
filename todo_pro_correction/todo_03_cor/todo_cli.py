#!/usr/bin/env python
# coding: utf-8
"""
対話式 Todo CLI（日本語）
依存: requests, python-dateparser
"""

import sqlite3
import requests
import sys
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import dateparser
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'todo.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        priority INTEGER,
        place_name TEXT,
        lat REAL,
        lon REAL,
        timezone TEXT,
        due_date TEXT,
        candidate_date TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    conn.close()


def add_task_interactive():
    print('\n--- タスク登録 ---')
    title = input('タイトル: ').strip()
    if not title:
        print('エラー: タイトルは必須です。')
        return

    # 優先度
    while True:
        pr = input('優先度（1:高, 2:中, 3:低）[2]: ').strip() or '2'
        if pr in ('1', '2', '3'):
            priority = int(pr)
            break
        print('エラー: 1,2,3 のいずれかで入力してください。')

    place = input('場所（都市名）: ').strip()
    if not place:
        print('エラー: 場所は必須です。')
        return

    geoinfo = geocode_place(place)
    if not geoinfo:
        print('エラー: 地名の解決に失敗しました。正しい都市名を指定してください。')
        return

    lat, lon, display = geoinfo
    tz = get_timezone_from_latlon(lat, lon)
    if not tz:
        print('警告: タイムゾーンを取得できませんでした。Asia/Tokyoを仮定します。')
        tz = 'Asia/Tokyo'

    # 期限入力（自然言語）
    while True:
        due_input = input('期限（日付、例: 2025-12-31, 明日, 来週の月曜）: ').strip()
        if not due_input:
            print('エラー: 期限は必須です。')
            continue
        due_dt = parse_date_with_tz(due_input, tz)
        if not due_dt:
            print('エラー: 日付の解析に失敗しました。別の表現を試してください。')
            continue
        due_date = due_dt.date()
        break

    # 候補日を選定
    candidate = choose_candidate_date(lat, lon, tz, date.today(), due_date)

    created_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO tasks (title, done, priority, place_name, lat, lon, timezone, due_date, candidate_date, created_at)
                 VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?, ?)
              ''', (title, priority, display, lat, lon, tz, due_date.isoformat(), candidate.isoformat() if candidate else None, created_at))
    conn.commit()
    task_id = c.lastrowid
    conn.close()

    print(f'登録しました。ID={task_id}')
    if candidate:
        print(f'候補日: {candidate.isoformat()}')
    else:
        print('候補日は見つかりませんでした。空き日の提案を確認してください。')


def list_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, done, priority, place_name, due_date, candidate_date FROM tasks ORDER BY due_date')
    rows = c.fetchall()
    conn.close()
    if not rows:
        print('\nタスクはありません。')
        return
    print('\n--- タスク一覧 ---')
    for r in rows:
        tid, title, done, pr, place, due, cand = r
        status = '完了' if done else '未完了'
        pr_str = {1:'高',2:'中',3:'低'}.get(pr,'-')
        print(f'ID:{tid} | {title} | 状態:{status} | 優先度:{pr_str} | 場所:{place} | 期限:{due} | 候補:{cand}')


def show_task_detail():
    tid = input('詳細を表示するタスクID: ').strip()
    if not tid.isdigit():
        print('エラー: 数値のIDを入力してください。')
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id=?', (int(tid),))
    row = c.fetchone()
    conn.close()
    if not row:
        print('エラー: タスクが見つかりません。')
        return
    keys = ['id','title','done','priority','place_name','lat','lon','timezone','due_date','candidate_date','created_at']
    print('\n--- タスク詳細 ---')
    for k, v in zip(keys, row):
        if k=='priority':
            v = {1:'高',2:'中',3:'低'}.get(v,'-')
        if k=='done':
            v = '完了' if v else '未完了'
        print(f'{k}: {v}')
    # 追加情報: 期限範囲の天気（候補日の気温など）
    tz = row[7]
    lat = row[5]
    lon = row[6]
    due = row[8]
    cand = row[9]
    if lat and lon and due:
        print('\n期限内の天気（簡易）:')
        start = date.today().isoformat()
        end = due
        w = fetch_weather_range(lat, lon, tz, start, end)
        if w:
            for d, info in w.items():
                print(f"{d} -> 降水確率:{info.get('precip_prob','-')}%  最高気温:{info.get('temp_max','-')}°C")


def update_task():
    tid = input('更新するタスクID: ').strip()
    if not tid.isdigit():
        print('エラー: 数値のIDを入力してください。')
        return
    tid = int(tid)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, done, priority, place_name, lat, lon, timezone, due_date FROM tasks WHERE id=?', (tid,))
    row = c.fetchone()
    if not row:
        print('エラー: タスクが見つかりません。')
        conn.close()
        return
    _, title, done, pr, place, lat, lon, tz, due = row
    print(f'現在のタイトル: {title}')
    new_title = input('新しいタイトル（空白で変更なし）: ').strip() or title
    print(f'現在の優先度: {pr}')
    new_pr = input('新しい優先度（1-3、空白で変更なし）: ').strip()
    if new_pr and new_pr not in ('1','2','3'):
        print('エラー: 優先度は1-3で入力してください。')
        conn.close()
        return
    new_pr = int(new_pr) if new_pr else pr
    print(f'現在の完了フラグ: {done} (1=完了)')
    new_done = input('完了にしますか？（y/n）: ').strip().lower()
    if new_done in ('y','yes'):
        # 完了ならタスク削除
        c.execute('DELETE FROM tasks WHERE id=?', (tid,))
        conn.commit()
        conn.close()
        print('タスクを完了として削除しました。')
        return
    # 期限変更
    new_due_input = input('新しい期限（空白で変更なし）: ').strip()
    if new_due_input:
        new_due_dt = parse_date_with_tz(new_due_input, tz)
        if not new_due_dt:
            print('エラー: 日付の解析に失敗しました。更新中止')
            conn.close()
            return
        new_due = new_due_dt.date()
    else:
        new_due = datetime.fromisoformat(due).date()

    # 候補日を再選定
    candidate = choose_candidate_date(lat, lon, tz, date.today(), new_due)

    c.execute('UPDATE tasks SET title=?, priority=?, due_date=?, candidate_date=? WHERE id=?', (new_title, new_pr, new_due.isoformat(), candidate.isoformat() if candidate else None, tid))
    conn.commit()
    conn.close()
    print('タスクを更新しました。')
    if candidate:
        print(f'新しい候補日: {candidate.isoformat()}')


def delete_task():
    tid = input('削除するタスクID: ').strip()
    if not tid.isdigit():
        print('エラー: 数値のIDを入力してください。')
        return
    tid = int(tid)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM tasks WHERE id=?', (tid,))
    if not c.fetchone():
        print('エラー: タスクが見つかりません。')
        conn.close()
        return
    c.execute('DELETE FROM tasks WHERE id=?', (tid,))
    conn.commit()
    conn.close()
    print('タスクを削除しました。')


def calendar_view():
    print('\n--- カレンダー表示 ---')
    year = input('表示する年（空白で今年）: ').strip()
    month = input('表示する月（1-12、空白で今月）: ').strip()
    try:
        if not year:
            year = date.today().year
        else:
            year = int(year)
        if not month:
            month = date.today().month
        else:
            month = int(month)
            if not (1 <= month <= 12):
                raise ValueError()
    except ValueError:
        print('エラー: 年月は数値で入力してください。')
        return
    # その月の1日と最終日
    start = date(year, month, 1)
    if month == 12:
        end = date(year+1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month+1, 1) - timedelta(days=1)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, title, due_date, candidate_date FROM tasks WHERE due_date BETWEEN ? AND ? ORDER BY due_date', (start.isoformat(), end.isoformat()))
    rows = c.fetchall()
    conn.close()
    if not rows:
        print('その月のタスクはありません。')
        return
    print(f'\n{year}年{month}月 のタスク')
    for r in rows:
        tid, title, due, cand = r
        print(f'ID:{tid} | {title} | 期限:{due} | 候補:{cand}')


# ----------------- ヘルパー: ジオコーディング・タイムゾーン・天気 -----------------

def geocode_place(place_name):
    """Nominatimで都市名を緯度経度に変換。返却: (lat, lon, display_name) または None"""
    url = 'https://nominatim.openstreetmap.org/search'
    params = {'q': place_name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'TodoCLI/1.0 (satosho311039@gmail.com)'}#実在のアドレスに変更
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        item = data[0]
        lat = float(item['lat'])
        lon = float(item['lon'])
        display = item.get('display_name', place_name)
        return lat, lon, display
    except Exception as e:
        return None


def get_timezone_from_latlon(lat, lon):
    """Open-Meteoのtimezone APIでタイムゾーン名を取得"""
    #URLとparamsに後ろの2つを追加
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {'latitude': lat, 'longitude': lon, 'timezone': 'auto', 'current_weather': 'true'}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        j = r.json()
        tz = j.get('timezone')
        return tz
    except Exception:
        return None


def fetch_weather_range(lat, lon, tz, start_date_str, end_date_str):
    """start/end in YYYY-MM-DD. 返却は日付->{precip_prob, temp_max}
    uses Open-Meteo daily=precipitation_probability_max,temperature_2m_max
    """
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'precipitation_probability_max,temperature_2m_max',
        'timezone': tz,
        'start_date': start_date_str,
        'end_date': end_date_str
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        j = r.json()
        dates = j.get('daily', {}).get('time', [])
        probs = j.get('daily', {}).get('precipitation_probability_max', [])
        temps = j.get('daily', {}).get('temperature_2m_max', [])
        out = {}
        for d, p, t in zip(dates, probs, temps):
            out[d] = {'precip_prob': p, 'temp_max': t}
        return out
    except Exception:
        return None


def parse_date_with_tz(text, tz_name):
    """日本語などの自然言語を、場所のタイムゾーン基準で解釈してdatetimeを返す"""
    try:
        base = datetime.now(ZoneInfo(tz_name))
    except Exception:
        base = datetime.now()
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': base,
        'RETURN_AS_TIMEZONE_AWARE': False,
    }
    try:
        dt = dateparser.parse(text, languages=['ja'], settings=settings)
        return dt
    except Exception:
        return None


def choose_candidate_date(lat, lon, tz, start_date, due_date):
    """期限内の最適な日を選ぶ。候補日は既存タスクと被らないようにする。
    戻り値: date オブジェクトか None
    """
    if start_date > due_date:
        return None
    start_iso = start_date.isoformat()
    end_iso = due_date.isoformat()
    weather = fetch_weather_range(lat, lon, tz, start_iso, end_iso)
    # 既存の候補日一覧を取得
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT candidate_date FROM tasks WHERE candidate_date IS NOT NULL')
    existing = set([r[0] for r in c.fetchall()])
    conn.close()

    if weather:
        # sort by precipitation prob asc, then temp desc
        choices = []
        for d, info in weather.items():
            prob = info.get('precip_prob')
            temp = info.get('temp_max')
            choices.append((prob if prob is not None else 100, -(temp if temp is not None else -999), d))
        choices.sort()
        for prob, negtemp, d in choices:
            if d in existing:
                continue
            # accept as candidate
            try:
                return datetime.fromisoformat(d).date()
            except Exception:
                continue
    # weatherが取得できない、または候補が見つからない場合、期限内で空いている日を探す
    cur = start_date
    while cur <= due_date:
        if cur.isoformat() not in existing:
            return cur
        cur += timedelta(days=1)
    # それでもなければ、期限後の直近7日で空き日を探す
    cur = due_date + timedelta(days=1)
    for _ in range(7):
        if cur.isoformat() not in existing:
            return cur
        cur += timedelta(days=1)
    return None


def main_loop():
    init_db()
    while True:
        print('\n--- Todo CLI メニュー ---')
        print('1) 登録  2) 一覧  3) 詳細  4) 更新  5) 削除  6) カレンダー表示  7) 終了')
        choice = input('選択: ').strip()
        if choice == '1':
            add_task_interactive()
        elif choice == '2':
            list_tasks()
        elif choice == '3':
            show_task_detail()
        elif choice == '4':
            update_task()
        elif choice == '5':
            delete_task()
        elif choice == '6':
            calendar_view()
        elif choice == '7':
            print('終了します。')
            sys.exit(0)
        else:
            print('不正な選択です。再度入力してください。')


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\n終了します。')
        sys.exit(0)
