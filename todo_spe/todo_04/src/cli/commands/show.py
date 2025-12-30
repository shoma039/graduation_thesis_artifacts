from src.storage import db
from rich import print
import json
import sys


def handle(args):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT t.*, l.user_input_name FROM task t LEFT JOIN location l ON t.location_id = l.id WHERE t.id = ?", (args.id,))
    r = cur.fetchone()
    if not r:
        msg = f"タスク {args.id} が見つかりません。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
            sys.exit(1)
        else:
            print(msg)
            return

    if getattr(args, "json", False):
        out = {k: r[k] for k in r.keys()}
        out["location"] = r.get("user_input_name")
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"ID: {r['id']}")
        print(f"タイトル: {r['title']}")
        print(f"期限(UTC): {r['deadline_utc']}")
        print(f"候補日(ローカル): {r['candidate_date_local']}")
        print(f"場所: {r['user_input_name']}")
