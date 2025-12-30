from typing import Dict, Any


def format_task_detail(task: Dict[str, Any]) -> str:
    """Return a Japanese-formatted multi-line detail view for a task dict.

    Expected keys in `task`: id, title, due_date, location (with name), candidate_dates (list)
    """
    lines = []
    lines.append(f"ID: {task.get('id')}")
    lines.append(f"タイトル: {task.get('title')}")
    lines.append(f"期限: {task.get('due_date')}")

    loc = task.get('location') or {}
    if loc:
        lines.append(f"場所: {loc.get('name')} ({loc.get('latitude')}, {loc.get('longitude')})")

    cands = task.get('candidate_dates', []) or []
    lines.append(f"候補日数: {len(cands)}")
    for i, c in enumerate(cands, start=1):
        date = c.get('date', '')
        precip = c.get('precipitation_probability')
        temp = c.get('temperature')
        reason = c.get('reason', '')
        lines.append(f"  {i}. {date} - 降水確率: {precip}% - 気温: {temp}°C - 理由: {reason}")

    return "\n".join(lines)
