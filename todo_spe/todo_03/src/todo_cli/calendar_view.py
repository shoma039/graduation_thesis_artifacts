import calendar
from datetime import datetime
from rich.table import Table
from rich.console import Console
from typing import List, Dict

console = Console()


def render_month(year: int, month: int, tasks: List[Dict]):
    """Render a simple monthly calendar with task markers.

    - `tasks` is a list of task dicts; each task may have `due_date` (YYYY-MM-DD)
      and `candidate_dates` list with `date` fields.
    """
    cal = calendar.Calendar(firstweekday=6)  # week starts Sunday
    month_days = cal.monthdayscalendar(year, month)

    # map date -> list of task summaries
    by_date = {}
    for t in tasks:
        if t.get("due_date"):
            try:
                d = datetime.fromisoformat(t["due_date"]) if len(t["due_date"])>10 else datetime.fromisoformat(t["due_date"]) 
            except Exception:
                d = None
            if d and d.year == year and d.month == month:
                by_date.setdefault(d.day, []).append(f"期限:{t.get('title')}")
        for c in t.get("candidate_dates", []):
            cd = c.get("date")
            try:
                d2 = datetime.fromisoformat(cd)
            except Exception:
                d2 = None
            if d2 and d2.year == year and d2.month == month:
                by_date.setdefault(d2.day, []).append(f"候補:{t.get('title')}")

    table = Table(title=f"{year}年 {month}月")
    for wd in ["日","月","火","水","木","金","土"]:
        table.add_column(wd, justify="center")

    for week in month_days:
        row = []
        for day in week:
            if day == 0:
                row.append("")
            else:
                marks = by_date.get(day, [])
                if marks:
                    row.append(f"{day} *{len(marks)}")
                else:
                    row.append(str(day))
        table.add_row(*row)

    console.print(table)

    # print details below
    if by_date:
        console.print("\n日別予定:")
        for day in sorted(by_date.keys()):
            console.print(f"{year}-{month:02d}-{day:02d}:")
            for desc in by_date[day]:
                console.print(f"  - {desc}")
