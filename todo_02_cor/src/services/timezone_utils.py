from zoneinfo import ZoneInfo

def zoneinfo_from_name(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except Exception:
        return ZoneInfo("UTC")
