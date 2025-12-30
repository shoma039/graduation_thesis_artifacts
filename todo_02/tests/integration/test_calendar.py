import sys
from pathlib import Path
import datetime
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.cli import main as cli_main
from src.db import db


def test_calendar_month_view(tmp_path):
    db_file = str(tmp_path / "test_cal.db")
    db.DB_PATH = db_file

    conn = db.connect(db_file)
    loc = {"name": "札幌", "latitude": 43.06, "longitude": 141.34, "timezone": "Asia/Tokyo"}
    loc_id = db.ensure_location(conn, loc)

    # Insert two tasks in December 2025 (example month)
    year = 2025
    month = 12
    d1 = datetime.date(year, month, 5).isoformat()
    d2 = datetime.date(year, month, 20).isoformat()

    # Insert tasks directly
    db.insert_task(conn, "カレンダー1", "medium", loc_id, datetime.datetime.now(datetime.timezone.utc), d1)
    db.insert_task(conn, "カレンダー2", "medium", loc_id, datetime.datetime.now(datetime.timezone.utc), d2)

    runner = CliRunner()
    res = runner.invoke(cli_main.app, ["todo", "calendar", "--month", f"{year}-{month:02d}"])
    assert res.exit_code == 0, res.output
    assert "カレンダー: 2025-12" in res.output
    assert "カレンダー1" in res.output
    assert "カレンダー2" in res.output
