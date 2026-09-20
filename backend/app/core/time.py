"""기상청 API와 저장된 관측시각은 모두 한국시간(KST) 기준이므로,
서버가 어느 시간대에서 돌아가든(Render는 UTC) 항상 KST wall-clock 기준의
naive datetime을 얻기 위한 헬퍼."""

from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def now_kst() -> datetime:
    return datetime.now(KST).replace(tzinfo=None)
