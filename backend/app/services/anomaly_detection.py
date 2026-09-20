"""통계 기반 이상치 탐지 + 과거 유사 사례 검색.

방식:
1. 같은 station/변수/월(계절성)별로 평균·표준편차를 구해 z-score 계산
2. |z| > threshold 인 값을 이상치로 표시
3. 이상치로 판정된 값과 절대값 차이가 tolerance 이내인 과거 관측을 유사 사례로 검색
"""

import pandas as pd

Z_SCORE_THRESHOLD = 3.0


def detect_anomalies(
    df: pd.DataFrame, variable: str, z_threshold: float = Z_SCORE_THRESHOLD
) -> pd.DataFrame:
    """df는 observed_at, station_id, {variable} 컬럼을 포함해야 한다.
    월별 평균/표준편차 기준 z-score로 이상치 여부(is_anomaly)와
    기대 범위(expected_low/high)를 계산해 반환한다.
    """
    data = df.dropna(subset=[variable]).copy()
    data["month"] = pd.to_datetime(data["observed_at"]).dt.month

    stats = data.groupby(["station_id", "month"])[variable].agg(["mean", "std"]).reset_index()
    data = data.merge(stats, on=["station_id", "month"], how="left")

    data["z_score"] = (data[variable] - data["mean"]) / data["std"].replace(0, pd.NA)
    data["is_anomaly"] = data["z_score"].abs() > z_threshold
    data["expected_low"] = data["mean"] - z_threshold * data["std"]
    data["expected_high"] = data["mean"] + z_threshold * data["std"]

    return data


def find_similar_past_events(
    history_df: pd.DataFrame,
    variable: str,
    value: float,
    tolerance: float,
    exclude_index: int | None = None,
) -> pd.DataFrame:
    """history_df 중 value와의 절대 차이가 tolerance 이내인 행을 유사 사례로 반환."""
    candidates = history_df.dropna(subset=[variable]).copy()
    if exclude_index is not None:
        candidates = candidates.drop(index=exclude_index, errors="ignore")
    candidates["diff"] = (candidates[variable] - value).abs()
    similar = candidates[candidates["diff"] <= tolerance].sort_values("diff")
    return similar
