from src.storage import db
from rich import print
import json
import sys


def handle(args):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM task WHERE id = ?", (args.id,))
    if not cur.fetchone():
        msg = f"タスク {args.id} が見つかりません。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
            sys.exit(1)
        else:
            print(msg)
            return
    cur.execute("DELETE FROM task WHERE id = ?", (args.id,))
    conn.commit()
    if getattr(args, "json", False):
        print(json.dumps({"result": "deleted", "id": args.id}, ensure_ascii=False))
    else:
        print(f"完了として削除しました: {args.id}")
