import typer
from src.cli.commands import app
from src.db import db


@app.command("show")
def show_task(task_id: int):
    """タスク詳細を表示する"""
    conn = db.connect()
    row = db.get_task(conn, task_id)
    if not row:
        typer.echo("タスクが見つかりません。")
        raise typer.Exit(code=1)
    typer.echo(f"ID: {row['id']}")
    typer.echo(f"タイトル: {row['title']}")
    typer.echo(f"優先度: {row['priority']}")
    typer.echo(f"候補日: {row['candidate_date']}")
    typer.echo(f"締切: {row['due_date']}")
    typer.echo(f"作成日時: {row['created_at']}")
