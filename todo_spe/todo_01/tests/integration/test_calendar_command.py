import subprocess
import sys
from pathlib import Path
from src.storage.store import Store


def run_todo(argv, cwd=None):
    # run via python -m src.cli.cli for integration simplicity
    cmd = [sys.executable, "-m", "src.cli.cli"] + argv
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def test_calendar_shows_tasks(tmp_path):
    store_path = tmp_path / "tasks.json"
    store = Store(store_path)
    # create tasks in 2026-01
    t1 = {"id": 1, "title": "会議", "due_date": "2026-01-05T09:00:00+09:00", "candidate_dates": []}
    t2 = {"id": 2, "title": "買い物", "due_date": "2026-01-15T10:00:00+09:00", "candidate_dates": []}
    store.add_task(t1)
    store.add_task(t2)

    code, out, err = run_todo(["--store", str(store_path), "calendar", "2026-01"]) 
    assert code == 0, f"Exit code non-zero: {err}"
    assert "2026年 1月" in out or "2026年 01月" in out
    assert "2026-01-05" in out
    assert "会議" in out
    assert "2026-01-15" in out
    assert "買い物" in out
