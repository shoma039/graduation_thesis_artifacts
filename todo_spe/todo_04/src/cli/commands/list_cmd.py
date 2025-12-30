from src.storage import db
from rich.table import Table
from rich.console import Console
import json


def _row_to_dict(r):
    return {
        "id": r["id"],
        "title": r["title"],
        "deadline_utc": r["deadline_utc"],
        "candidate_date_local": r["candidate_date_local"],
        "priority": r["priority"],
        "location": r["user_input_name"],
    }


def handle(args):
    conn = db.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT t.id, t.title, t.deadline_utc, t.candidate_date_local, t.priority, l.user_input_name FROM task t LEFT JOIN location l ON t.location_id = l.id ORDER BY deadline_utc")
    rows = cur.fetchall()
    console = Console()
    table = Table(title="Tasks")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Deadline")
    table.add_column("Candidate")
    table.add_column("Priority")
    table.add_column("Location")
    for r in rows:
        table.add_row(str(r['id']), r['title'], r['deadline_utc'] or '', r['candidate_date_local'] or '', r['priority'] or '', r['user_input_name'] or '')

    if getattr(args, "json", False):
        out = [ _row_to_dict(r) for r in rows ]
        print(json.dumps(out, ensure_ascii=False))
    else:
        console.print(table)
