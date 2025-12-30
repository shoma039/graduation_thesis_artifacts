import requests
from datetime import date, timedelta
from typing import Dict, Any

OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast'

def fetch_daily_forecast(lat: float, lon: float, tz: str, start: date, end: date) -> Dict[str, Dict[str, Any]]:
    """指定期間の日次予報を取得し、日付ごとに降水確率と最高/最低気温を返す。
    返り値: { 'YYYY-MM-DD': { 'precip_prob': value, 'temp_max': v, 'temp_min': v } }
    """
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max',
        'timezone': tz,
        'start_date': start.isoformat(),
        'end_date': end.isoformat()
    }
    try:
        r = requests.get(OPEN_METEO_BASE, params=params, timeout=10)
        r.raise_for_status()
        j = r.json()
        daily = j.get('daily', {})
        dates = daily.get('time', [])
        precip = daily.get('precipitation_probability_max', [])
        tmax = daily.get('temperature_2m_max', [])
        tmin = daily.get('temperature_2m_min', [])
        out = {}
        for i, d in enumerate(dates):
            out[d] = {
                'precip_prob': precip[i] if i < len(precip) else None,
                'temp_max': tmax[i] if i < len(tmax) else None,
                'temp_min': tmin[i] if i < len(tmin) else None,
            }
        return out
    except Exception:
        return {}
