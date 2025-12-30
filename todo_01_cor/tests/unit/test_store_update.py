from src.storage.store import Store
from pathlib import Path
import json


def test_add_update_remove_flow(tmp_path):
    store_path = tmp_path / "tasks.json"
    store = Store(store_path)

    # start with empty
    assert store.list_tasks() == []

    # add a task
    task = {"id": 1, "title": "テスト", "priority": "中", "due_date": "2026-01-05T09:00:00+09:00", "candidate_dates": []}
    store.add_task(task)
    t = store.get_task(1)
    assert t is not None
    assert t["title"] == "テスト"

    # update title and priority
    ok = store.update_task(1, {"title": "買い物", "priority": "高"})
    assert ok
    t2 = store.get_task(1)
    assert t2 is not None
    assert t2["title"] == "買い物"
    assert t2["priority"] == "高"

    # ensure backup files created
    backups = list((store_path.parent / "backups").glob("tasks_backup_*.json"))
    assert len(backups) >= 1

    # complete (remove)
    ok2 = store.remove_task(1)
    assert ok2
    assert store.get_task(1) is None

    # history log exists
    hist = store_path.parent / "backups" / "history.log"
    assert hist.exists()
    with open(hist, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    assert any('"op": "remove"' in l or '"op": "update"' in l for l in lines)
