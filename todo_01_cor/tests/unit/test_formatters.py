from src.utils.formatters import format_task_detail


def make_sample_task():
    return {
        'id': 'task-1',
        'title': '買い物',
        'due_date': '2025-12-10T18:00:00+09:00',
        'location': {
            'name': '渋谷',
            'latitude': 35.6595,
            'longitude': 139.7005,
        },
        'candidate_dates': [
            {
                'date': '2025-12-10T09:00:00+09:00',
                'precipitation_probability': 10,
                'temperature': 15,
                'reason': '晴れで候補',
            },
            {
                'date': '2025-12-11T09:00:00+09:00',
                'precipitation_probability': 60,
                'temperature': 12,
                'reason': '小雨が予想される',
            },
        ],
    }


def test_format_task_detail_includes_core_fields():
    t = make_sample_task()
    out = format_task_detail(t)
    assert 'ID: task-1' in out
    assert 'タイトル: 買い物' in out
    assert '期限: 2025-12-10T18:00:00+09:00' in out
    assert '場所: 渋谷' in out


def test_format_task_detail_lists_candidates():
    t = make_sample_task()
    out = format_task_detail(t)
    # should list two candidates with precipitation and temperature
    assert '候補日数: 2' in out
    assert '1. 2025-12-10T09:00:00+09:00 - 降水確率: 10% - 気温: 15°C - 理由: 晴れで候補' in out
    assert '2. 2025-12-11T09:00:00+09:00 - 降水確率: 60% - 気温: 12°C - 理由: 小雨が予想される' in out
