from src.services import geocode, weather, scheduler, date_parser
from src.storage import db
import json
import sys
from rich import print


def handle(args):
    title = args.title
    deadline_raw = args.deadline
    location_name = args.location
    priority = args.priority

    # parse date
    parsed = date_parser.parse_japanese_date(deadline_raw)
    if not parsed:
        msg = "日付の解析に失敗しました。入力を確認してください。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"エラー: {msg}")
        sys.exit(1)

    # geocode
    loc = geocode.geocode_location(location_name)
    if not loc:
        msg = "場所のジオコーディングに失敗しました。都市名を確認してください。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"エラー: {msg}")
        sys.exit(1)

    # schedule
    candidate = scheduler.pick_candidate_date(loc, parsed)
    if not candidate:
        msg = "候補日を見つけられませんでした。予備日を検討してください。"
        if getattr(args, "json", False):
            print(json.dumps({"error": msg}, ensure_ascii=False))
            sys.exit(1)
        else:
            print(f"警告: {msg}")

    # save task
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task (title, priority, location_id, deadline_utc, candidate_date_local, status, created_at, updated_at) VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))",
        (title, priority, loc['id'], parsed.isoformat(), candidate['date'], 'open'),
    )
    conn.commit()
    task_id = cur.lastrowid

    if getattr(args, "json", False):
        out = {"id": task_id, "title": title, "candidate": candidate}
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"作成しました: ID={task_id} 候補日: {candidate['date']} 降水確率: {candidate.get('precip', 'N/A')}% 気温: {candidate.get('temp','N/A')}°C")
