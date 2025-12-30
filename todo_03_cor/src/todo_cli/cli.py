import argparse
from datetime import datetime

from .config import get_data_path
from .formatters import print_task_list, format_task_summary
from .calendar_view import render_month
from ..services.storage import Storage
from ..services.geocode import geocode_place
from ..services.date_parser import parse_natural_date
from ..models.validation import validate_due_date_not_past
from ..services.scheduler import Scheduler


def cmd_add(args):
    print("新しいタスクを作成します。入力してください。")
    title = input("タイトル: ").strip()
    if not title:
        print("タイトルは必須です。")
        return
    due_input = input("期限（例: 明日, 来週の月曜）: ").strip()
    location_input = input("場所（都市名）: ").strip()
    priority_input = input("優先度 (高/中/低) [既定: 中]: ").strip() or "中"
    # ユーザー向けに日本語で受け付け、内部は英語 key を使う
    pri_map = {"高": "high", "高い": "high", "中": "medium", "中くらい": "medium", "低": "low", "低い": "low",
               "high": "high", "medium": "medium", "low": "low"}
    priority = pri_map.get(priority_input, "medium")
    try:
        geo = geocode_place(location_input)
    except Exception as e:
        print(f"都市解決エラー: {e}")
        return
    try:
        dt = parse_natural_date(due_input, tz=geo.get("timezone", "UTC"))
    except Exception as e:
        print(f"日付解釈エラー: {e}")
        return
    try:
        validate_due_date_not_past(dt)
    except Exception as e:
        print(f"期限エラー: {e}")
        return
    due_date = dt.date().isoformat()
    storage = Storage()
    scheduler = Scheduler(storage)
    candidate = scheduler.pick_candidate(geo["latitude"], geo["longitude"], geo["timezone"], dt.date())
    task = {
        "title": title,
        "completed": False,
        "priority": priority,
        "location": geo,
        "due_date": due_date,
        "candidate_dates": [candidate] if candidate else [],
    }
    task_id = storage.add_task(task)
    print(f"タスクを保存しました。ID: {task_id}")
    print(format_task_summary({**task, "id": task_id}))


def cmd_list(args):
    storage = Storage()
    tasks = storage.list_tasks()
    print_task_list(tasks)


def cmd_show(args):
    storage = Storage()
    t = storage.get_task(int(args.id))
    if not t:
        print("タスクが見つかりません。")
        return
    print(t)


def cmd_complete(args):
    storage = Storage()
    ok = storage.delete_task(int(args.id))
    if ok:
        print("タスクを完了として削除しました。")
    else:
        print("タスクが見つかりません。")


def cmd_update(args):
    storage = Storage()
    task_id = int(args.id)
    t = storage.get_task(task_id)
    if not t:
        print("タスクが見つかりません。")
        return
    print("更新: 空エンターで現在値を保持します。")
    title = input(f"タイトル [{t.get('title')}]: ").strip() or t.get('title')
    location_input = input(f"場所 [{t.get('location', {}).get('name') if t.get('location') else ''}]: ").strip()
    if location_input:
        try:
            geo = geocode_place(location_input)
        except Exception as e:
            print(f"都市解決エラー: {e}")
            return
    else:
        geo = t.get('location')
    due_input = input(f"期限 [{t.get('due_date')}]: ").strip()
    if due_input:
        try:
            dt = parse_natural_date(due_input, tz=geo.get('timezone', 'UTC'))
        except Exception as e:
            print(f"日付解釈エラー: {e}")
            return
    else:
        dt = None
    priority_input = input(f"優先度 (高/中/低) [{t.get('priority')}]: ").strip() or t.get('priority')
    pri_map = {"高": "high", "高い": "high", "中": "medium", "中くらい": "medium", "低": "low", "低い": "low",
               "high": "high", "medium": "medium", "low": "low"}
    priority = pri_map.get(priority_input, t.get('priority'))

    updates = {"title": title, "priority": priority, "location": geo}
    if dt:
        from ..models.validation import validate_due_date_not_past
        try:
            validate_due_date_not_past(dt)
        except Exception as e:
            print(f"期限エラー: {e}")
            return
        updates["due_date"] = dt.date().isoformat()

    # if due_date or location changed, recalc candidate
    recalc = False
    if dt or (geo and geo != t.get('location')):
        recalc = True
    if recalc:
        scheduler = Scheduler(storage)
        lat = geo.get('latitude')
        lon = geo.get('longitude')
        tz = geo.get('timezone')
        due = dt.date() if dt else datetime.fromisoformat(t.get('due_date')).date()
        candidate = scheduler.pick_candidate(lat, lon, tz, due)
        updates['candidate_dates'] = [candidate] if candidate else []

    ok = storage.update_task(task_id, updates)
    if ok:
        print("タスクを更新しました。")
    else:
        print("更新に失敗しました。")


def cmd_delete(args):
    storage = Storage()
    task_id = int(args.id)
    confirm = input(f"タスク {task_id} を削除してよろしいですか？ (y/N): ").strip().lower()
    if confirm != 'y':
        print("削除をキャンセルしました。")
        return
    ok = storage.delete_task(task_id)
    if ok:
        print("タスクを削除しました。")
    else:
        print("タスクが見つかりません。")


def cmd_calendar(args):
    import datetime
    storage = Storage()
    month_arg = getattr(args, 'month', None)
    if month_arg:
        try:
            y, m = map(int, month_arg.split('-'))
        except Exception:
            print("月指定は YYYY-MM 形式で指定してください。例: 2025-12")
            return
    else:
        now = datetime.datetime.now()
        y, m = now.year, now.month
    tasks = storage.list_tasks()
    render_month(y, m, tasks)


def main():
    parser = argparse.ArgumentParser(prog="todo")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("add")
    sub.add_parser("list")
    p_show = sub.add_parser("show")
    p_show.add_argument("id")
    p_complete = sub.add_parser("complete")
    p_complete.add_argument("id")
    p_update = sub.add_parser("update")
    p_update.add_argument("id")
    p_delete = sub.add_parser("delete")
    p_delete.add_argument("id")
    p_calendar = sub.add_parser("calendar")
    p_calendar.add_argument("--month", help="月を指定します。YYYY-MM形式で。")
    args = parser.parse_args()
    if args.cmd == "add":
        cmd_add(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "show":
        cmd_show(args)
    elif args.cmd == "complete":
        cmd_complete(args)
    elif args.cmd == "update":
        cmd_update(args)
    elif args.cmd == "delete":
        cmd_delete(args)
    elif args.cmd == "calendar":
        cmd_calendar(args)
    else:
        parser.print_help()
