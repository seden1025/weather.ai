"""기상자료개방포털(data.kma.go.kr) API 클라이언트 - 종관기상관측(ASOS) 시간자료.

필드 순서는 실제 API 응답으로 검증함 (kma_sfctm2.php?...&help=0 호출 결과):

  TM STN WD WS GST_WD GST_WS GST_TM PA PS PT PR TA TD HM PV
  RN RN_DAY RN_JUN RN_INT SD_HR3 SD_DAY SD_TOT WC WP WW
  CA_TOT CA_MID CH_MIN CT CT_TOP CT_MID CT_LOW VS SS SI ST_GD
  TS TE_005 TE_01 TE_02 TE_03 ST_SEA WH BF IR IX

결측치는 -9 / -9.0 / -9.00 같은 sentinel 값으로 내려온다.
"""

from datetime import datetime

import httpx
import pandas as pd

from app.core.config import settings

ASOS_HOURLY_URL = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php"  # 시간자료(기간 조회), 최대 31일

# 0-based index into 공백으로 split한 필드 목록
FIELD_TM = 0
FIELD_STN = 1
FIELD_WS = 3
FIELD_PA = 7
FIELD_TA = 11
FIELD_HM = 13
FIELD_RN = 15


class KmaClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.kma_api_key

    async def get_asos_hourly(
        self, station_id: str, start: datetime, end: datetime
    ) -> pd.DataFrame:
        """지점(station_id)의 시간별 지상관측자료(ASOS)를 조회한다. 최대 31일 범위."""
        params = {
            "tm1": start.strftime("%Y%m%d%H%M"),
            "tm2": end.strftime("%Y%m%d%H%M"),
            "stn": station_id,
            "authKey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(ASOS_HOURLY_URL, params=params)
            resp.raise_for_status()
            return self._parse_asos_hourly(resp.text)

    @staticmethod
    def _parse_asos_hourly(raw_text: str) -> pd.DataFrame:
        rows = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) <= FIELD_RN:
                continue
            rows.append(
                {
                    "station_id": fields[FIELD_STN],
                    "observed_at": pd.to_datetime(fields[FIELD_TM], format="%Y%m%d%H%M"),
                    "temperature": _safe_float(fields[FIELD_TA]),
                    "precipitation": _safe_float(fields[FIELD_RN]),
                    "wind_speed": _safe_float(fields[FIELD_WS]),
                    "humidity": _safe_float(fields[FIELD_HM]),
                    "pressure": _safe_float(fields[FIELD_PA]),
                }
            )
        return pd.DataFrame(rows)


def _safe_float(value: str) -> float | None:
    try:
        f = float(value)
    except ValueError:
        return None
    # 결측치 sentinel은 정확히 -9 계열 값 (실제 혹한 기온 -9.0도와 구분하기 위해 등호 비교)
    return None if f == -9.0 or f == -9 else f
