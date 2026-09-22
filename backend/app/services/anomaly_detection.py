"""통계 기반 이상치 탐지.

지점 x 변수 x 월별 평년 평균/표준편차(climatology.json, scripts/compute_climatology.py로
로컬 5년 데이터에서 미리 계산해둔 값)를 기준으로, 새로 들어온 관측값의 z-score가
임계값을 넘으면 이상치로 판정한다. 운영 DB에 몇 년치 원본 데이터를 다시
넣지 않고도 "평년과 얼마나 다른지"를 즉시 계산할 수 있다.
"""

import json
from pathlib import Path

CLIMATOLOGY_PATH = Path(__file__).resolve().parent / "climatology.json"
Z_SCORE_THRESHOLD = 3.0

_climatology_cache: dict | None = None


def _load_climatology() -> dict:
    global _climatology_cache
    if _climatology_cache is None:
        if CLIMATOLOGY_PATH.exists():
            _climatology_cache = json.loads(CLIMATOLOGY_PATH.read_text(encoding="utf-8"))
        else:
            _climatology_cache = {}
    return _climatology_cache


def check_anomaly(
    station_id: str, variable: str, month: int, value: float, z_threshold: float = Z_SCORE_THRESHOLD
) -> dict | None:
    """value가 해당 지점/변수/월의 평년 대비 이상치인지 확인한다.

    이상치가 아니거나 평년값 데이터가 없으면 None, 이상치면
    {z_score, expected_low, expected_high}를 반환한다.
    """
    stats = _load_climatology().get(f"{station_id}:{variable}:{month}")
    if not stats or not stats.get("std"):
        return None

    mean, std = stats["mean"], stats["std"]
    z = (value - mean) / std
    if abs(z) <= z_threshold:
        return None

    return {
        "z_score": round(z, 2),
        "expected_low": round(mean - z_threshold * std, 2),
        "expected_high": round(mean + z_threshold * std, 2),
    }
