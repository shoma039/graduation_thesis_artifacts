from src.storage import db
from src.services import geocode, scheduler, date_parser
from rich import print
import json
import sys


def handle(args):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (args.id,))
    task = cur.fetchone()
    if not task:
        msg = f"タスク {args.id} が見つかりません。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
            sys.exit(1)
        else:
            print(msg)
            return

    title = args.title or task['title']
    priority = args.priority or task['priority']
    deadline = task['deadline_utc']
    if args.deadline:
        parsed = date_parser.parse_japanese_date(args.deadline)
        if not parsed:
            msg = "日付解析に失敗しました"
            if getattr(args, "json", False):
                print(json.dumps({"error": msg}, ensure_ascii=False))
                sys.exit(1)
            else:
                print(msg)
                return
        deadline = parsed.isoformat()

    location_id = task['location_id']
    if args.location:
        loc = geocode.geocode_location(args.location)
        if not loc:
            msg = "場所のジオコーディングに失敗しました"
            if getattr(args, "json", False):
                print(json.dumps({"error": msg}, ensure_ascii=False))
                sys.exit(1)
            else:
                print(msg)
                return
        location_id = loc['id']

    # update
    cur.execute("UPDATE task SET title = ?, priority = ?, deadline_utc = ?, location_id = ?, updated_at = datetime('now') WHERE id = ?",
                (title, priority, deadline, location_id, args.id))
    conn.commit()
    # recompute candidate
    cur.execute("SELECT * FROM location WHERE id = ?", (location_id,))
    loc = cur.fetchone()
    if loc:
        candidate = scheduler.pick_candidate_date(dict(loc), date_parser.parse_japanese_date(deadline))
        if candidate:
            cur.execute("UPDATE task SET candidate_date_local = ? WHERE id = ?", (candidate['date'], args.id))
            conn.commit()

    if getattr(args, "json", False):
        print(json.dumps({"result": "updated", "id": args.id}, ensure_ascii=False))
    else:
        print(f"更新しました: {args.id}")
