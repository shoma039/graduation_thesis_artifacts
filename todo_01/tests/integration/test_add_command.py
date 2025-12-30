import json
import tempfile
from pathlib import Path
from src.cli.cli import main


def test_add_command_end_to_end(monkeypatch, tmp_path):
    # Prepare a temporary store path
    store_file = tmp_path / "tasks_test.json"

    # Mock geocode to return a known location
    def mock_geocode(place_name):
        return [{"name": "Tokyo", "latitude": 35.6895, "longitude": 139.6917}]

    # Mock timezone_for
    def mock_timezone(lat, lon):
        return "Asia/Tokyo"

    # Mock candidate selector to return deterministic candidate
    def mock_select_candidate_dates(due_iso, location, max_candidates=1):
        return [{"date": "2026-01-05T09:00:00+09:00", "precipitation_probability": 5, "temperature": 10, "reason": "low_precip"}]

    # Patch the functions referenced by the CLI module directly
    monkeypatch.setattr("src.cli.cli.geocode_place", mock_geocode)
    monkeypatch.setattr("src.cli.cli.timezone_for", mock_timezone)
    monkeypatch.setattr("src.cli.cli.select_candidate_dates", mock_select_candidate_dates)

    # Run CLI add
    # Note: global options (like --store) must come before the subcommand
    argv = [
        "--store",
        str(store_file),
        "add",
        "--title",
        "公園清掃",
        "--due",
        "2026-01-05T09:00",
        "--priority",
        "高",
        "--location",
        "東京",
    ]
    main(argv)

    # Verify store content
    assert store_file.exists()
    data = json.loads(store_file.read_text(encoding="utf-8"))
    tasks = data.get("tasks", [])
    assert len(tasks) == 1
    t = tasks[0]
    assert t.get("title") == "公園清掃"
    assert t.get("candidate_dates") and len(t.get("candidate_dates")) == 1
