import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import db
from src.cli.commands import list as list_cmd
from datetime import datetime

db_file = str(ROOT / "debug_test.db")
db.DB_PATH = db_file
conn = db.connect(db_file)
loc_id = db.ensure_location(conn, {"name": "X", "latitude": 1.0, "longitude": 2.0, "timezone": "UTC"})
db.insert_task(conn, "t1", "medium", loc_id, datetime.utcnow(), None)

print('About to call list_tasks')
list_cmd.list_tasks()
