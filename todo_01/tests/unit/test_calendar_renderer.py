from src.utils.calendar_renderer import render_month


def test_render_month_shows_task_days():
    tasks = [
        {"id": 1, "title": "会議", "due_date": "2026-01-05T09:00:00+09:00", "location": {}},
        {"id": 2, "title": "買い物", "due_date": "2026-01-15T10:00:00+09:00", "location": {}},
    ]
    out = render_month(2026, 1, tasks, timezone="Asia/Tokyo")
    assert "2026年 1月" in out
    assert "05*" in out or " 5*" in out
    assert "15*" in out or "15*" in out
    assert "2026-01-05" in out
    assert "会議" in out
        # Removed stray end-patch marker