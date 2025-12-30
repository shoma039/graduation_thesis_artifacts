import json
from pathlib import Path
from typing import Any, Optional


class Cache:
    def __init__(self, name: str, dir_path: Optional[Path] = None):
        self.name = name
        self.dir = dir_path or Path('.cache')
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"{name}.json"
        self._data = None

    def _load(self):
        if self._data is not None:
            return
        if not self.path.exists():
            self._data = {}
            return
        try:
            with self.path.open('r', encoding='utf-8') as f:
                self._data = json.load(f)
        except Exception:
            self._data = {}

    def get(self, key: str) -> Optional[Any]:
        self._load()
        return self._data.get(key)

    def set(self, key: str, value: Any):
        self._load()
        self._data[key] = value
        try:
            with self.path.open('w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
