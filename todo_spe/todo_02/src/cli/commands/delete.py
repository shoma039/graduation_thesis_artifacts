import typer
from src.cli.commands import app
from src.db import db


@app.command("delete")
def delete_task(task_id: int):
    """タスクを削除する"""
    conn = db.connect()
    row = db.get_task(conn, task_id)
    if not row:
        typer.echo("タスクが見つかりません。")
        raise typer.Exit(code=1)
    db.delete_task(conn, task_id)
    typer.echo(f"タスク {task_id} を削除しました。")
