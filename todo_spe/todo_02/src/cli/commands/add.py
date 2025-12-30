from datetime import datetime
import typer

from src.cli.commands import app
from src.services import parser as date_parser
from src.services import geocode, scheduler
from src.db import db
from src.lib.errors import UserError


@app.command("add")
def add_task(
    title: str = typer.Option(..., help="タイトル"),
    location: str = typer.Option(..., help="都市名"),
    due: str = typer.Option(..., help="期限（自然言語可）"),
    priority: str = typer.Option("medium", help="low|medium|high"),
):
    """タスクを追加し、候補日を算出して表示する"""
    # Resolve location first to get correct timezone context for due date parsing
    loc = geocode.geocode_location(location)
    try:
        due_dt = date_parser.parse_natural_date(due, timezone=loc.get("timezone"))
    except Exception as e:
        raise UserError(f"日付解析に失敗しました: {e}")
    # create location in DB or get existing
    conn = db.connect()
    loc_id = db.ensure_location(conn, loc)

    # scheduler selects candidate date
    candidate = scheduler.select_candidate_for_location(conn, loc_id, due_dt)
    candidate_label = "候補日"
    if candidate is None:
        # try proposing an alternative after due date
        alt = scheduler.propose_alternative_date(conn, loc_id, due_dt)
        if alt:
            candidate = alt
            candidate_label = "予備日"
        else:
            # fallback to due date itself
            candidate = due_dt.date().isoformat()

    task_id = db.insert_task(conn, title, priority, loc_id, due_dt, candidate)

    typer.echo(f"タスク作成: ID={task_id}\nタイトル: {title}\n{candidate_label}: {candidate}")
