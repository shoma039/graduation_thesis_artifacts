import sys
from pathlib import Path
import datetime
import tempfile
from typer.testing import CliRunner

# Ensure project root is importable as a package (so `src` can be imported)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.cli import main as cli_main
from src.db import db
from src.services import geocode, weather


def test_crud_flow(monkeypatch, tmp_path):
    # Use a temporary sqlite file for isolation
    db_file = str(tmp_path / "test.db")
    db.DB_PATH = db_file

    # Patch external services to avoid network calls
    monkeypatch.setattr(geocode, "geocode_location", lambda name: {"name": name, "latitude": 43.06, "longitude": 141.34, "timezone": "Asia/Tokyo"})
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    monkeypatch.setattr(weather, "fetch_daily_forecast", lambda lat, lon, start_date, end_date, timezone="UTC": [{"date": tomorrow, "precipitation_prob": 10.0, "temp_min": -1.0, "temp_max": 5.0}])

    runner = CliRunner()

    # Add a task via CLI
    res = runner.invoke(cli_main.app, ["todo", "add", "--title", "テスト", "--location", "札幌", "--due", "明日"])
    assert res.exit_code == 0, res.output
    assert "タスク作成" in res.output

    # List tasks and ensure the created task appears
    res2 = runner.invoke(cli_main.app, ["todo", "list"])
    assert res2.exit_code == 0
    assert "テスト" in res2.output

    # Read DB directly to get the ID
    conn = db.connect(db_file)
    rows = db.list_tasks(conn)
    assert len(rows) >= 1
    task_id = rows[0]["id"]

    # Show task
    res3 = runner.invoke(cli_main.app, ["todo", "show", str(task_id)])
    assert res3.exit_code == 0
    assert "タイトル: テスト" in res3.output

    # Mark complete via update (deletes task)
    res4 = runner.invoke(cli_main.app, ["todo", "update", str(task_id), "--complete"]) 
    assert res4.exit_code == 0
    assert "完了扱い" in res4.output or "削除しました" in res4.output

    # Show should now fail
    res5 = runner.invoke(cli_main.app, ["todo", "show", str(task_id)])
    assert res5.exit_code != 0
