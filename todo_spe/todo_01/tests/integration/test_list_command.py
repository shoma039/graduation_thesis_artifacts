import json
from src.cli.cli import main


def test_list_command_shows_tasks_sorted(tmp_path, capsys):
    store_file = tmp_path / "tasks_list.json"
    data = {
        "tasks": [
            {
                "id": 1,
                "title": "A タスク",
                "due_date": "2026-01-10T09:00:00+09:00",
                "candidate_dates": [],
            },
            {
                "id": 2,
                "title": "B タスク",
                "due_date": "2026-01-05T09:00:00+09:00",
                "candidate_dates": [
                    {"date": "2026-01-05T09:00:00+09:00", "precipitation_probability": 5, "temperature": 10}
                ],
            },
        ]
    }
    store_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # run list
    main(["--store", str(store_file), "list"])
    out = capsys.readouterr().out.strip().splitlines()

    assert len(out) >= 2
    # first line should be task with earlier due date (id 2)
    assert out[0].startswith("ID:2")
    assert "タイトル:B タスク" in out[0]
    # second line should be id 1
    assert out[1].startswith("ID:1")
    assert "タイトル:A タスク" in out[1]


def test_list_command_empty_store_shows_message(tmp_path, capsys):
    store_file = tmp_path / "empty.json"
    store_file.write_text(json.dumps({"tasks": []}, ensure_ascii=False), encoding="utf-8")

    main(["--store", str(store_file), "list"])
    out = capsys.readouterr().out.strip()
    assert out == "タスクはありません。"
