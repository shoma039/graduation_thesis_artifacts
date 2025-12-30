import sys
from datetime import datetime, timedelta

sys.path.insert(0, "src")

from services import date_parser


def test_parse_japanese_tomorrow():
    dt = date_parser.parse_japanese_date("明日")
    assert dt is not None
    assert isinstance(dt, datetime)
    # parsed date should be after now
    assert dt.date() >= (datetime.now().date())
