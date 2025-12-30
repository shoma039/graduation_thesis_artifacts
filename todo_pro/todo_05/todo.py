#!/usr/bin/env python
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys

from models import Task, Location
import storage
import geocode
import weather
import utils

def input_nonempty(prompt: str) -> str:
    s = input(prompt).strip()
    while not s:
        print('入力が空です。もう一度入力してください。')
        s = input(prompt).strip()
    return s

def cmd_add(tasks: List[Task]):
    print('--- タスク登録 ---')
    title = input_nonempty('タイトル: ')
    pr = input('優先度 (1=高,2=中,3=低) [2]: ').strip() or '2'
    try:
        prn = int(pr)
        if prn not in (1,2,3):
            raise ValueError()
    except Exception:
        print('優先度は1〜3の整数で指定してください。中(2)を使用します。')
        prn = 2
    loc_name = input('場所（都市名、空欄で未設定）: ').strip()
    location = None
    if loc_name:
        res = geocode.geocode_city(loc_name)
        if not res:
            print('場所の取得に失敗しました。場所は未設定になります。')
        else:
            display, lat, lon, tz = res
            location = Location(name=display, latitude=lat, longitude=lon, timezone=tz)
            print(f'場所: {display} (lat={lat}, lon={lon}, tz={tz})')
    # deadline
    tz = location.timezone if location else 'UTC'
    dl_text = input('期限（例: 明日, 2025-12-10, 来週の月曜。空欄で未設定）: ').strip()
    dl_date = None
    if dl_text:
        parsed = utils.parse_natural_date(dl_text, tz)
        if not parsed:
            print('日付の解析に失敗しました。期限は未設定になります。')
        else:
            dl_date = parsed
            print(f'期限: {dl_date.isoformat()} (タイムゾーン: {tz})')

    nid = storage.next_id(tasks)
    now = datetime.utcnow().isoformat()
    task = Task(id=nid, title=title, done=False, priority=prn, location=location, deadline=dl_date.isoformat() if dl_date else None, candidate_date=None, created_at=now)

    # 候補日選定
    if location and dl_date:
        start = date.today()
        end = dl_date
        if end < start:
            print('期限が過去です。候補日は設定しません。')
        else:
            forecasts = weather.fetch_daily_forecast(location.latitude, location.longitude, location.timezone, start, end)
            if not forecasts:
                print('天気予報を取得できませんでした。候補日は設定しません。')
            else:
                items = [(d, v['precip_prob'] if v['precip_prob'] is not None else 100, v) for d, v in forecasts.items()]
                items.sort(key=lambda x: (x[1], x[0]))
                assigned = None
                used_dates = {t.candidate_date for t in tasks if t.candidate_date}
                for d, pp, info in items:
                    if d in used_dates:
                        continue
                    assigned = (d, pp, info)
                    break
                if assigned:
                    d, pp, info = assigned
                    task.candidate_date = d
                    print(f'候補日を自動選択しました: {d} (降水確率 {pp}%, 最高 {info.get("temp_max")}℃ 最低 {info.get("temp_min")}℃)')
                else:
                    cur = start
                    proposed = None
                    while cur <= end:
                        s = cur.isoformat()
                        if s not in used_dates:
                            proposed = s
                            break
                        cur += timedelta(days=1)
                    if proposed:
                        task.candidate_date = proposed
                        print(f'候補日の重複が多かったため、空いている日を提案: {proposed}')
                    else:
                        print('期限内で候補日を割り当てられませんでした。')

    tasks.append(task)
    storage.save_tasks(tasks)
    print(f'タスクを追加しました (ID={task.id})')

def cmd_list(tasks: List[Task]):
    if not tasks:
        print('タスクは登録されていません。')
        return
    print('--- タスク一覧 ---')
    for t in sorted(tasks, key=lambda x: (x.candidate_date or x.deadline or '9999-99-99', -x.priority)):
        status = '完了' if t.done else '未完'
        cand = t.candidate_date or '-'
        dl = t.deadline or '-'
        loc = t.location.name if t.location else '-'
        print(f'ID:{t.id} | {t.title} | 優先度:{t.priority} | 状態:{status} | 候補日:{cand} | 期限:{dl} | 場所:{loc}')

def find_task(tasks: List[Task], tid: int) -> Optional[Task]:
    for t in tasks:
        if t.id == tid:
            return t
    return None

def cmd_show(tasks: List[Task]):
    try:
        tid = int(input('表示するタスクID: ').strip())
    except Exception:
        print('IDは整数で入力してください。')
        return
    t = find_task(tasks, tid)
    if not t:
        print('指定のタスクは見つかりません。')
        return
    print('--- タスク詳細 ---')
    print(f'ID: {t.id}')
    print(f'タイトル: {t.title}')
    print(f'優先度: {t.priority}')
    print(f'状態: {"完了" if t.done else "未完"}')
    print(f'期限: {t.deadline or "未設定"}')
    print(f'候補日: {t.candidate_date or "未設定"}')
    if t.location:
        print(f'場所: {t.location.name} (lat={t.location.latitude}, lon={t.location.longitude}, tz={t.location.timezone})')

def cmd_update(tasks: List[Task]):
    try:
        tid = int(input('更新するタスクID: ').strip())
    except Exception:
        print('IDは整数で入力してください。')
        return
    t = find_task(tasks, tid)
    if not t:
        print('指定のタスクは見つかりません。')
        return
    print('Enter で既存値を保持します。')
    new_title = input(f'タイトル [{t.title}]: ').strip() or t.title
    new_pr = input(f'優先度 (1-3) [{t.priority}]: ').strip() or str(t.priority)
    try:
        new_prn = int(new_pr)
        if new_prn not in (1,2,3):
            raise ValueError()
    except Exception:
        print('優先度が不正です。既存値を使用します。')
        new_prn = t.priority
    loc_name = input('場所（都市名、空欄で変更なし、-で削除）: ').strip()
    if loc_name == '-':
        t.location = None
    elif loc_name:
        res = geocode.geocode_city(loc_name)
        if res:
            display, lat, lon, tz = res
            t.location = Location(name=display, latitude=lat, longitude=lon, timezone=tz)
            print(f'場所更新: {display}')
        else:
            print('場所の取得に失敗しました。場所は変更しません。')
    dl_text = input(f'期限 [{t.deadline or "未設定"}]: ').strip()
    if dl_text:
        tz = t.location.timezone if t.location else 'UTC'
        parsed = utils.parse_natural_date(dl_text, tz)
        if parsed:
            t.deadline = parsed.isoformat()
            print(f'期限を更新しました: {t.deadline}')
        else:
            print('日付解析に失敗しました。期限は変更しません。')
    done_text = input(f'完了にする？ (y/N) [現在: {"完了" if t.done else "未完"}]: ').strip().lower()
    t.title = new_title
    t.priority = new_prn
    if done_text == 'y':
        # 完了になったら削除する
        tasks.remove(t)
        storage.save_tasks(tasks)
        print('タスクは完了として削除されました。')
        return
    storage.save_tasks(tasks)
    print('タスクを更新しました。')

def cmd_delete(tasks: List[Task]):
    try:
        tid = int(input('削除するタスクID: ').strip())
    except Exception:
        print('IDは整数で入力してください。')
        return
    t = find_task(tasks, tid)
    if not t:
        print('指定のタスクは見つかりません。')
        return
    confirm = input(f'タスク「{t.title}」を削除しますか？ (y/N): ').strip().lower()
    if confirm == 'y':
        tasks.remove(t)
        storage.save_tasks(tasks)
        print('削除しました。')
    else:
        print('削除をキャンセルしました。')

def cmd_calendar(tasks: List[Task]):
    ym = input('表示する年月 (YYYY-MM、空欄で今月): ').strip()
    if not ym:
        today = date.today()
        year = today.year
        month = today.month
    else:
        try:
            parts = ym.split('-')
            year = int(parts[0]); month = int(parts[1])
        except Exception:
            print('年月の形式が正しくありません。')
            return
    # 月の初日と末日
    first = date(year, month, 1)
    if month == 12:
        last = date(year+1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month+1, 1) - timedelta(days=1)
    mapping = {}
    for t in tasks:
        if t.candidate_date:
            mapping.setdefault(t.candidate_date, []).append(t)
        elif t.deadline:
            mapping.setdefault(t.deadline, []).append(t)
    cur = first
    print(f'--- {year}年{month}月 のタスク ---')
    while cur <= last:
        s = cur.isoformat()
        if s in mapping:
            print(f'{s}:')
            for tt in mapping[s]:
                print(f'  - ID:{tt.id} {tt.title} (優先度:{tt.priority}) 場所:{tt.location.name if tt.location else "-"}')
        cur += timedelta(days=1)

def main():
    tasks = storage.load_tasks()
    print('Todo CLI アプリ (日本語)。コマンド help で一覧。')
    while True:
        cmd = input('\nコマンド (add/list/show/update/delete/calendar/quit/help): ').strip().lower()
        if cmd == 'add':
            cmd_add(tasks)
        elif cmd == 'list':
            cmd_list(tasks)
        elif cmd == 'show':
            cmd_show(tasks)
        elif cmd == 'update':
            cmd_update(tasks)
        elif cmd == 'delete':
            cmd_delete(tasks)
        elif cmd == 'calendar':
            cmd_calendar(tasks)
        elif cmd == 'help':
            print('利用可能なコマンド: add, list, show, update, delete, calendar, quit')
        elif cmd in ('quit', 'exit'):
            print('終了します。')
            break
        else:
            print('不明なコマンドです。help を参照してください。')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n終了しました。')
