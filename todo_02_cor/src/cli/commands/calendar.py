from datetime import date, datetime, timedelta
import typer

from src.cli.commands import app
from src.db import db


@app.command("calendar")
def calendar_view(month: str = typer.Option(None, help="Month in YYYY-MM format. Default: current month")):
    """Show a month view of tasks (候補日 and due dates) for the specified month."""
    if month:
        try:
            year, mon = month.split("-")
            year = int(year)
            mon = int(mon)
            start = date(year, mon, 1)
        except Exception:
            typer.echo("無効な月フォーマットです。例: 2025-12")
            raise typer.Exit(code=1)
    else:
        today = date.today()
        start = date(today.year, today.month, 1)

    # compute end as last day of month
    if start.month == 12:
        next_month = date(start.year + 1, 1, 1)
    else:
        next_month = date(start.year, start.month + 1, 1)
    end = next_month - timedelta(days=1)

    conn = db.connect()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM tasks
        WHERE (date(candidate_date) BETWEEN ? AND ?) OR (date(due_date) BETWEEN ? AND ?)
        ORDER BY date(candidate_date) ASC, created_at ASC
        """,
        (start.isoformat(), end.isoformat(), start.isoformat(), end.isoformat()),
    )
    rows = cur.fetchall()

    if not rows:
        typer.echo(f"{start.strftime('%Y-%m')} のタスクはありません。")
        return

    # Group by date (candidate_date preferred, else due_date)
    groups = {}
    for r in rows:
        cand = r["candidate_date"]
        due = r["due_date"]
        key = None
        if cand:
            key = cand[:10]
        elif due:
            key = due[:10]
        else:
            key = "unknown"
        groups.setdefault(key, []).append(r)

    typer.echo(f"カレンダー: {start.strftime('%Y-%m')}")
    for d in sorted(groups.keys()):
        typer.echo(f"\n{d}")
        for r in groups[d]:
            tid = r["id"]
            title = r["title"]
            cand = r["candidate_date"] or "-"
            due = r["due_date"] or "-"
            typer.echo(f" - ID={tid} タイトル: {title} 候補日: {cand} 期限: {due}")
