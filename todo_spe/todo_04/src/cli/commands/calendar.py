from src.storage import db
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta


def handle(args):
    month = args.month  # YYYY-MM
    try:
        dt = datetime.fromisoformat(month + "-01")
    except Exception:
        print("月指定の形式は YYYY-MM です")
        return
    conn = db.get_conn()
    cur = conn.cursor()
    start = dt.strftime("%Y-%m-01")
    # naive end: next month first day minus one
    if dt.month == 12:
        nextm = datetime(dt.year + 1, 1, 1)
    else:
        nextm = datetime(dt.year, dt.month + 1, 1)
    end = (nextm - timedelta(days=1)).strftime("%Y-%m-%d")

    # Join forecastsample to include precip/temperature for candidate dates
    cur.execute(
        """
        SELECT t.title, t.candidate_date_local, t.priority, l.user_input_name,
               fs.precip_probability AS precip, fs.temperature_c AS temp
        FROM task t
        LEFT JOIN location l ON t.location_id = l.id
        LEFT JOIN forecastsample fs ON fs.location_id = l.id AND fs.date_local = t.candidate_date_local
        WHERE t.candidate_date_local BETWEEN ? AND ?
        ORDER BY t.candidate_date_local
        """,
        (start, end),
    )
    rows = cur.fetchall()
    console = Console()
    table = Table(title=f"Calendar {month}")
    table.add_column("Date")
    table.add_column("Title")
    table.add_column("Priority")
    table.add_column("Location")
    table.add_column("Precip%")
    table.add_column("Temp(°C)")
    for r in rows:
        precip = ''
        temp = ''
        if r['precip'] is not None:
            # format as integer percentage if possible
            try:
                precip = f"{int(r['precip'])}%"
            except Exception:
                precip = str(r['precip'])
        if r['temp'] is not None:
            try:
                temp = f"{float(r['temp']):.1f}°C"
            except Exception:
                temp = str(r['temp'])
        table.add_row(r['candidate_date_local'] or '', r['title'], r['priority'] or '', r['user_input_name'] or '', precip, temp)
    console.print(table)
