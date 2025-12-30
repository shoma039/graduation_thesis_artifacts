from datetime import datetime, date, timedelta
from . import output
from ..services import storage


def month_view(year_month: str):
    """Render a simple month view for YYYY-MM"""
    try:
        dt = datetime.strptime(year_month, '%Y-%m')
    except Exception:
        print(output.error('無効な年月フォーマット。YYYY-MM を指定してください'))
        return

    start = date(dt.year, dt.month, 1)
    if dt.month == 12:
        end = date(dt.year + 1, 1, 1)
    else:
        end = date(dt.year, dt.month + 1, 1)

    start_iso = start.isoformat()
    # inclusive end date is end - 1 day
    last_day = end - timedelta(days=1)
    end_iso = last_day.isoformat()

    items = storage.list_candidate_dates_in_range(start_iso, end_iso)
    if not items:
        print(output.info('該当月の候補日は見つかりません'))
        return

    print(output.info(f"--- {year_month} の候補日一覧 ---"))
    for it in items:
        print(output.line(f"{it['date']}: タスク={it.get('title')} (候補ID={it.get('id')}) 確定={'はい' if it.get('is_confirmed') else 'いいえ'} 場所={it.get('display_name') or '-'} 予報降水={it.get('expected_precipitation')}"))
