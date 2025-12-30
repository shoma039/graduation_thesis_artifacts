import argparse
from pathlib import Path
from datetime import datetime, timedelta
from src.storage.store import Store
from src.models.task import Task, Location, CandidateDate
from src.services.geocoding import geocode_place
from src.services.timezone import timezone_for
from src.scheduler.candidate_selector import select_candidate_dates
from src.utils.parse_date import parse_date, to_iso
from src.utils.errors import ParseError, ServiceError, StorageError
from src.utils.logging import setup_logging, get_logger
import traceback
from src.utils.calendar_renderer import render_month
from zoneinfo import ZoneInfo
from datetime import datetime

logger = get_logger(__name__)


def _validate_priority(p: str) -> str:
    allowed = ["高", "中", "低"]
    if p not in allowed:
        raise ParseError(f"優先度は {','.join(allowed)} のいずれかで指定してください。 (受け取った: {p})")
    return p


def cmd_add(args):
    store = Store(Path(args.store) if args.store else None)
    nid = store.next_id()
    loc = None
    if args.location:
        # try geocode
        candidates = geocode_place(args.location)
        if candidates:
            chosen = candidates[0]
            tz = timezone_for(chosen["latitude"], chosen["longitude"]) or "UTC"
            loc = Location(name=chosen.get("name", args.location), latitude=chosen.get("latitude"), longitude=chosen.get("longitude"), timezone=tz)
        else:
            loc = Location(name=args.location)

    # validate inputs
    try:
        if not args.title or not args.title.strip():
            raise ParseError("タイトルを入力してください。")
        priority = _validate_priority(args.priority)
    except ParseError as e:
        print(f"入力エラー: {e}")
        return

    due_iso = None
    if args.due:
        try:
            dt = parse_date(args.due, timezone=(loc.timezone if loc and getattr(loc, 'timezone', None) else None))
            if dt is None:
                raise ParseError("期限の解析に失敗しました。日本語表現か ISO 形式を指定してください。")
            due_iso = to_iso(dt)
        except ParseError as e:
            print(f"期限の解析エラー: {e}")
            return
        except Exception as e:
            print("期限の解析中に予期せぬエラーが発生しました。詳細をログで確認してください。")
            logger.exception("date parse error")
            return

    task = Task(id=nid, title=args.title, priority=args.priority, location=loc, due_date=due_iso)

    # candidate selection if possible
    try:
        if task.due_date and task.location and task.location.latitude and task.location.longitude:
            cands = select_candidate_dates(task.due_date, {"latitude": task.location.latitude, "longitude": task.location.longitude, "timezone": task.location.timezone or "UTC"}, max_candidates=1)
            for c in cands:
                task.candidate_dates.append(CandidateDate(date=c["date"], precipitation_probability=c.get("precipitation_probability"), temperature=c.get("temperature"), reason=c.get("reason")))
    except ServiceError as e:
        print(f"候補日取得サービスでエラーが発生しました: {e}")
        logger.exception("candidate selection service error")
    except Exception as e:
        print("候補日の自動選定で予期せぬエラーが発生しました。ログを確認してください。")
        logger.exception("unexpected candidate selection error")

    store.add_task(task.to_dict())
    print(f"タスクを追加しました (ID: {nid})")


def cmd_list(args):
    store = Store(Path(args.store) if args.store else None)
    tasks = store.list_tasks()
    if not tasks:
        print("タスクはありません。")
        return
    # sort by due_date if present
    def key_fn(t):
        return t.get("due_date") or ""
    tasks = sorted(tasks, key=key_fn)
    for t in tasks:
        print(f"ID:{t.get('id')}  タイトル:{t.get('title')}  期限:{t.get('due_date')}  候補:{len(t.get('candidate_dates', []))}")


def cmd_show(args):
    store = Store(Path(args.store) if args.store else None)
    t = store.get_task(int(args.id))
    if not t:
        print(f"ID {args.id} のタスクが見つかりません。")
        return
    print(json_pretty(t))


def cmd_delete(args):
    store = Store(Path(args.store) if args.store else None)
    ok = store.remove_task(int(args.id))
    if ok:
        print(f"タスク {args.id} を削除しました。")
    else:
        print(f"タスク {args.id} は見つかりませんでした。")


def json_pretty(d):
    import json

    return json.dumps(d, ensure_ascii=False, indent=2)


def cmd_update(args):
    store = Store(Path(args.store) if args.store else None)
    tid = int(args.id)
    updates = {}
    if args.title:
        updates["title"] = args.title
    if args.priority:
        try:
            _validate_priority(args.priority)
            updates["priority"] = args.priority
        except Exception as e:
            print(f"優先度エラー: {e}")
            return
    if args.due:
        try:
            dt = parse_date(args.due, timezone=None)
            if dt is None:
                print("期限の解析に失敗しました。")
                return
            updates["due_date"] = to_iso(dt)
        except Exception:
            print("期限解析中にエラーが発生しました。")
            return

    ok = store.update_task(tid, updates)
    if ok:
        print(f"タスク {tid} を更新しました。")
    else:
        print(f"タスク {tid} が見つかりませんでした。")


def cmd_complete(args):
    store = Store(Path(args.store) if args.store else None)
    tid = int(args.id)
    ok = store.remove_task(tid)
    if ok:
        print(f"タスク {tid} を完了として削除しました。")
    else:
        print(f"タスク {tid} が見つかりませんでした。")


def cmd_calendar(args):
    store = Store(Path(args.store) if args.store else None)
    # parse month arg YYYY-MM
    if args.month:
        try:
            parts = args.month.split("-")
            year = int(parts[0])
            month = int(parts[1])
        except Exception:
            print("月指定は YYYY-MM の形式でお願いします。例: 2026-01")
            return
    else:
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        year = now.year
        month = now.month

    tasks = store.list_tasks()
    out = render_month(year, month, tasks, timezone="Asia/Tokyo")
    print(out)


def main(argv=None):
    setup_logging()
    parser = argparse.ArgumentParser(prog="todo")
    parser.add_argument("--store", help="ストアファイルのパス（省略時デフォルト）")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="タスクを追加")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--due", required=False)
    p_add.add_argument("--priority", default="中")
    p_add.add_argument("--location", required=False)
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="タスク一覧")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="タスク詳細")
    p_show.add_argument("id")
    p_show.set_defaults(func=cmd_show)

    p_del = sub.add_parser("delete", help="タスクを削除")
    p_del.add_argument("id")
    p_del.set_defaults(func=cmd_delete)

    p_update = sub.add_parser("update", help="タスクを更新")
    p_update.add_argument("id")
    p_update.add_argument("--title", required=False)
    p_update.add_argument("--due", required=False)
    p_update.add_argument("--priority", required=False)
    p_update.set_defaults(func=cmd_update)

    p_complete = sub.add_parser("complete", help="タスクを完了にして削除")
    p_complete.add_argument("id")
    p_complete.set_defaults(func=cmd_complete)

    p_calendar = sub.add_parser("calendar", help="月次カレンダー表示 (YYYY-MM)")
    p_calendar.add_argument("month", nargs="?", help="対象月を YYYY-MM 形式で指定（省略時は今月）")
    p_calendar.set_defaults(func=cmd_calendar)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
