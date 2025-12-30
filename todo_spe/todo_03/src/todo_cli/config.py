import os
from pathlib import Path


def get_data_path() -> Path:
    """Return path to tasks.json (platform-aware)."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            base = Path(appdata) / "todo-cli-scheduler"
        else:
            base = Path.home() / "AppData" / "Roaming" / "todo-cli-scheduler"
    else:
        base = Path.home() / ".local" / "share" / "todo-cli-scheduler"
    base.mkdir(parents=True, exist_ok=True)
    return base / "tasks.json"
