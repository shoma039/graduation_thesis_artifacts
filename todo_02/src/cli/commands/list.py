from typing import Optional
import typer
from src.cli.commands import app
from src.db import db


@app.command("list")
def list_tasks(sort: Optional[str] = typer.Option("date", help="date|priority|created")):
    """タスク一覧を表示する"""
    conn = db.connect()
    rows = db.list_tasks(conn, sort)
    if not rows:
        typer.echo("タスクはありません。")
        return
    for r in rows:
        typer.echo(f"ID={r['id']} | {r['title']} | 候補日={r['candidate_date']} | 締切={r['due_date']} | 優先度={r['priority']}")
