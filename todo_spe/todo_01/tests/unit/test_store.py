import tempfile
from pathlib import Path
import json

from src.storage.store import Store


def test_add_and_get_and_remove(tmp_path):
    fp = tmp_path / "tasks.json"
    store = Store(fp)
    assert store.list_tasks() == []

    # add a task
    task = {"id": 1, "title": "test", "completed": False, "candidate_dates": []}
    store.add_task(task)
    all_tasks = store.list_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0]["title"] == "test"

    # get
    t = store.get_task(1)
    assert t is not None
    assert t["id"] == 1

    # remove
    ok = store.remove_task(1)
    assert ok
    assert store.list_tasks() == []
