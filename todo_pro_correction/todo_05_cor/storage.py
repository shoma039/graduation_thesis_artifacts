import json
from typing import List
from pathlib import Path
from models import Task

DATA_FILE = Path(__file__).parent / 'tasks.json'

def load_tasks() -> List[Task]:
    if not DATA_FILE.exists():
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [Task.from_dict(d) for d in data]
    except Exception:
        return []

def save_tasks(tasks: List[Task]):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)

def next_id(tasks: List[Task]) -> int:
    if not tasks:
        return 1
    return max(t.id for t in tasks) + 1
