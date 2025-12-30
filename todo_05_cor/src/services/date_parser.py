from typing import Optional
from datetime import datetime
import dateparser
from zoneinfo import ZoneInfo


def parse_natural_date(text: str, tz_str: str = 'UTC') -> Optional[datetime]:
    """Parse natural-language date/time (Japanese supported) and return timezone-aware datetime.

    Returns None if parsing fails.
    """
    if not text:
        return None

    # ▼▼▼ 修正: RELATIVE_BASE 用の現在時刻を計算する ▼▼▼
    try:
        # 指定されたタイムゾーンでの現在時刻を取得
        base_date = datetime.now(ZoneInfo(tz_str))
    except Exception:
        # タイムゾーン指定がおかしい場合はシステム時刻をバックアップとして使う
        base_date = datetime.now()
    # ▲▲▲ ここまで ▲▲▲

    settings = {
        'RETURN_AS_TIMEZONE_AWARE': True,
        'TO_TIMEZONE': tz_str,
        'PREFER_DATES_FROM': 'future',
        # ▼▼▼ 修正: None ではなく日付オブジェクトを渡す ▼▼▼
        'RELATIVE_BASE': base_date, 
    }
    
    try:
        dt = dateparser.parse(text, languages=['ja', 'en'], settings=settings)
    except Exception:
        return None

    if dt is None:
        return None

    # Ensure tzinfo is set
    if dt.tzinfo is None:
        try:
            dt = dt.replace(tzinfo=ZoneInfo(tz_str))
        except Exception:
            pass
    return dt


def parse_natural_date_iso(text: str, tz_str: str = 'UTC') -> Optional[str]:
    dt = parse_natural_date(text, tz_str)
    if dt is None:
        return None
    return dt.isoformat()