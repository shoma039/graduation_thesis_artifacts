from rich.table import Table
from rich.console import Console
from typing import List, Dict

console = Console()


def format_task_summary(t: Dict) -> str:
    pri_map = {"high": "高", "medium": "中", "low": "低"}
    p = pri_map.get(t.get('priority'), t.get('priority'))
    return f"[{t.get('id')}] {t.get('title')} (期限: {t.get('due_date')}) 優先度: {p}"


def print_task_list(tasks: List[Dict]):
    # sort by due_date (None last)
    def sort_key(t):
        d = t.get("due_date")
        return (d is None, d)
    tasks_sorted = sorted(tasks, key=sort_key)
    table = Table(title="タスク一覧")
    table.add_column("ID", justify="right")
    table.add_column("タイトル")
    table.add_column("期限")
    table.add_column("優先度")
    pri_map = {"high": "高", "medium": "中", "low": "低"}
    for t in tasks_sorted:
        p = pri_map.get(t.get("priority"), t.get("priority") or "")
        table.add_row(str(t.get("id")), t.get("title", ""), str(t.get("due_date", "")), p)
    console.print(table)
