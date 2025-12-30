import json
from pathlib import Path
from typing import Dict, Any, List

from ..models.task import Task, CandidateDate
from ..todo_cli.config import get_data_path
from .utils import atomic_write, read_json_file


class Storage:
    def __init__(self, path: Path = None):
        self.path = path or get_data_path()
        self._data = None

    def load_all(self) -> Dict[str, Any]:
        data = read_json_file(self.path)
        if data is None:
            data = {"tasks": [], "next_id": 1, "locations": []}
        self._data = data
        return data

    def save_all(self):
        if self._data is None:
            self._data = {"tasks": [], "next_id": 1, "locations": []}
        atomic_write(self.path, json.dumps(self._data, ensure_ascii=False, indent=2))

    def add_task(self, task_dict: Dict[str, Any]) -> int:
        data = self._data or self.load_all()
        task_id = data.get("next_id", 1)
        task_dict["id"] = task_id
        data.setdefault("tasks", []).append(task_dict)
        data["next_id"] = task_id + 1
        self.save_all()
        return task_id

    def update_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        data = self._data or self.load_all()
        for t in data.get("tasks", []):
            if t.get("id") == task_id:
                t.update(updates)
                self.save_all()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        data = self._data or self.load_all()
        tasks = data.get("tasks", [])
        for i, t in enumerate(tasks):
            if t.get("id") == task_id:
                tasks.pop(i)
                self.save_all()
                return True
        return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        data = self._data or self.load_all()
        return data.get("tasks", [])

    def get_task(self, task_id: int) -> Dict[str, Any]:
        for t in (self._data or self.load_all()).get("tasks", []):
            if t.get("id") == task_id:
                return t
        return None
