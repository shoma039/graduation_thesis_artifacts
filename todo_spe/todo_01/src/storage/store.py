import json
from pathlib import Path
from typing import List, Optional
import os
from filelock import FileLock


DEFAULT_PATH = Path(os.path.expandvars(r"%USERPROFILE%")) / ".todo_weather_cli" / "tasks.json"
DEFAULT_LOCK = DEFAULT_PATH.with_suffix(".lock")


class Store:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self.lock_path = self.path.with_suffix(".lock")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # backups directory for undo/history
        self.backups_dir = self.path.parent / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        # initialize file if missing
        if not self.path.exists():
            self._write_data({"tasks": []})

    def _read_data(self) -> dict:
        lock = FileLock(str(self.lock_path))
        with lock:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write_data(self, data: dict) -> None:
        lock = FileLock(str(self.lock_path))
        with lock:
            # write atomically
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def list_tasks(self) -> List[dict]:
        data = self._read_data()
        tasks = data.get("tasks", [])

        # Enrich each task with a simple candidate summary for CLI display
        for t in tasks:
            cands = t.get("candidate_dates", []) or []
            if not cands:
                t["candidate_summary"] = "候補: 0件"
            else:
                # choose the first candidate as the "best" for summary (assumes selector orders by best)
                best = cands[0]
                # derive a short date (YYYY-MM-DD) for readability
                date_str = best.get("date", "")
                if date_str:
                    short = date_str.split("T")[0]
                else:
                    short = ""
                t["candidate_summary"] = f"候補: {len(cands)}件 (最良: {short})"

        # Sort tasks by due_date (ISO string). Tasks without due_date sort after dated ones.
        def sort_key(x):
            d = x.get("due_date")
            return d or "~"  # tilde sorts after typical ISO dates

        return sorted(tasks, key=sort_key)

    def _write_backup(self, snapshot: dict, op: str, task_id: Optional[int] = None) -> Path:
        """Write a timestamped backup of the given snapshot and log the op."""
        from datetime import datetime, timezone

        # use timezone-aware UTC now to avoid deprecation warnings
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        fname = f"tasks_backup_{ts}.json"
        path = self.backups_dir / fname
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"op": op, "task_id": task_id, "snapshot": snapshot}, f, ensure_ascii=False, indent=2)
        # append to history log
        hist = self.backups_dir / "history.log"
        with open(hist, "a", encoding="utf-8") as h:
            entry = {"ts": ts, "op": op, "task_id": task_id, "file": str(path)}
            h.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return path

    def next_id(self) -> int:
        tasks = self.list_tasks()
        if not tasks:
            return 1
        return max(t.get("id", 0) for t in tasks) + 1

    def add_task(self, task_dict: dict) -> dict:
        data = self._read_data()
        # backup before mutation
        self._write_backup(data, op="add", task_id=task_dict.get("id"))
        tasks = data.get("tasks", [])
        tasks.append(task_dict)
        data["tasks"] = tasks
        self._write_data(data)
        return task_dict

    def get_task(self, id: int) -> Optional[dict]:
        for t in self.list_tasks():
            if t.get("id") == id:
                return t
        return None

    def remove_task(self, id: int) -> bool:
        data = self._read_data()
        tasks = data.get("tasks", [])
        # backup before mutation
        self._write_backup(data, op="remove", task_id=id)
        new = [t for t in tasks if t.get("id") != id]
        if len(new) == len(tasks):
            return False
        data["tasks"] = new
        self._write_data(data)
        return True

    def update_task(self, id: int, updates: dict) -> bool:
        """Update fields of a task by id. Returns True if updated."""
        data = self._read_data()
        tasks = data.get("tasks", [])
        found = False
        for t in tasks:
            if t.get("id") == id:
                found = True
                break
        if not found:
            return False
        # backup before mutation
        self._write_backup(data, op="update", task_id=id)
        for k, v in updates.items():
            # prevent changing id
            if k == "id":
                continue
            # replace or remove key if value is None
            if v is None and k in t:
                t.pop(k, None)
            else:
                t[k] = v
        data["tasks"] = tasks
        self._write_data(data)
        return True
