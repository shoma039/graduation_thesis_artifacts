import sys
from datetime import datetime

sys.path.insert(0, "src")

from util import date_utils


def test_local_date_to_utc_iso_tokyo():
    # Tokyo is UTC+9: local midnight should be previous day 15:00 UTC
    iso = date_utils.local_date_to_utc_iso("2025-12-10", "Asia/Tokyo")
    assert iso.startswith("2025-12-09T15:00")


def test_isoformat_utc_roundtrip():
    now = datetime(2025, 12, 10, 12, 0, 0)
    s = date_utils.isoformat_utc(now)
    assert "2025-12-10" in s
