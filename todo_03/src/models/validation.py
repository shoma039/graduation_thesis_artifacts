from datetime import datetime


def validate_due_date_not_past(due_dt: datetime) -> None:
    """Raise ValueError if the given timezone-aware datetime is before today in its timezone.

    due_dt: timezone-aware datetime returned from date parser (tzinfo set)
    """
    if due_dt.tzinfo is None:
        # defensively treat as UTC
        now = datetime.utcnow().date()
        due_date = due_dt.date()
    else:
        now = datetime.now(due_dt.tzinfo).date()
        due_date = due_dt.astimezone(due_dt.tzinfo).date()
    if due_date < now:
        raise ValueError("期限が過去日です。未来の日付を指定してください。")
