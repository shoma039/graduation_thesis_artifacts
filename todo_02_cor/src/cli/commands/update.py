import typer
from src.cli.commands import app
from src.services import parser as date_parser, geocode
from src.db import db


@app.command("update")
def update_task(
    task_id: int,
    title: str = typer.Option(None),
    location: str = typer.Option(None),
    due: str = typer.Option(None),
    priority: str = typer.Option(None),
    complete: bool = typer.Option(False),
):
    """タスクを更新する。--complete true で完了（削除）。"""
    conn = db.connect()
    task = db.get_task(conn, task_id)
    if not task:
        typer.echo("タスクが見つかりません。")
        raise typer.Exit(code=1)

    if complete:
        db.delete_task(conn, task_id)
        typer.echo(f"タスク {task_id} を完了扱いとして削除しました。")
        return

    updates = {}
    if title:
        updates['title'] = title
    if priority:
        updates['priority'] = priority
    if due:
        due_dt = date_parser.parse_natural_date(due)
        updates['due_date'] = due_dt
    if location:
        loc = geocode.geocode_location(location)
        loc_id = db.ensure_location(conn, loc)
        updates['location_id'] = loc_id

    if updates:
        db.update_task(conn, task_id, updates)
        typer.echo(f"タスク {task_id} を更新しました。")
    else:
        typer.echo("更新項目が指定されていません。")
