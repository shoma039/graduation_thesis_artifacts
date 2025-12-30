import pytest
from types import SimpleNamespace

import src.services.scheduler as scheduler


def test_assigns_best_free_date(monkeypatch):
    task = {
        'id': 1,
        'lat': 35.0,
        'lon': 139.0,
        'timezone': 'Asia/Tokyo',
        'deadline': '2025-12-11T00:00:00+09:00',
        'created_at': '2025-12-01T00:00:00'
    }

    monkeypatch.setattr('src.services.storage.get_task', lambda tid: task)
    monkeypatch.setattr('src.services.storage.get_candidate_dates_on_date', lambda date: [])

    inserted = []

    def fake_insert(task_id, date, is_confirmed=0, expected_precipitation=None, expected_temperature=None):
        inserted.append((task_id, date, expected_precipitation, expected_temperature))
        return 1

    monkeypatch.setattr('src.services.storage.insert_candidate_date', fake_insert)

    def fake_forecast(lat, lon, start_date, end_date, timezone=None):
        return [
            {'date': '2025-12-10', 'precip_probability': 10, 'temp_max': 15},
            {'date': '2025-12-11', 'precip_probability': 20, 'temp_max': 12},
        ]

    monkeypatch.setattr('src.services.weather.get_daily_forecast', fake_forecast)

    res = scheduler.generate_candidates_for_task(1, max_candidates=1)

    assert res['assigned'], 'Expected an assigned candidate'
    assert res['assigned'][0]['date'] == '2025-12-10'
    assert inserted[0][1] == '2025-12-10'


def test_conflict_eviction_prefers_earlier_registered(monkeypatch):
    # existing candidate belongs to task 2 created later than task 1
    task = {
        'id': 1,
        'lat': 35.0,
        'lon': 139.0,
        'timezone': 'Asia/Tokyo',
        'deadline': '2025-12-11T00:00:00+09:00',
        'created_at': '2025-12-01T00:00:00'
    }

    existing = [{'id': 5, 'task_id': 2, 'date': '2025-12-10', 'created_at': '2025-12-02T00:00:00'}]

    monkeypatch.setattr('src.services.storage.get_task', lambda tid: task)
    monkeypatch.setattr('src.services.storage.get_candidate_dates_on_date', lambda date: existing if date == '2025-12-10' else [])

    evicted = []

    def fake_delete(evicted_task_id):
        evicted.append(evicted_task_id)

    monkeypatch.setattr('src.services.storage.delete_candidate_dates_for_task', fake_delete)

    inserted = []

    def fake_insert(task_id, date, is_confirmed=0, expected_precipitation=None, expected_temperature=None):
        inserted.append((task_id, date))
        return 1

    monkeypatch.setattr('src.services.storage.insert_candidate_date', fake_insert)

    def fake_forecast(lat, lon, start_date, end_date, timezone=None):
        return [{'date': '2025-12-10', 'precip_probability': 10, 'temp_max': 15}]

    monkeypatch.setattr('src.services.weather.get_daily_forecast', fake_forecast)

    res = scheduler.generate_candidates_for_task(1, max_candidates=1)

    # since existing was created later than current task, eviction should occur
    assert evicted and evicted[0] == 2
    assert inserted and inserted[0][1] == '2025-12-10'


def test_no_forecast_returns_empty(monkeypatch):
    task = {
        'id': 3,
        'lat': 0.0,
        'lon': 0.0,
        'timezone': 'UTC',
        'deadline': '2025-12-05T00:00:00+00:00',
        'created_at': '2025-12-01T00:00:00'
    }

    monkeypatch.setattr('src.services.storage.get_task', lambda tid: task)
    monkeypatch.setattr('src.services.weather.get_daily_forecast', lambda lat, lon, s, e, timezone=None: [])

    res = scheduler.generate_candidates_for_task(3, max_candidates=1)
    assert res['assigned'] == []
    assert res['alternatives'] == []
