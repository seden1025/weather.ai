"""기온 예측을 위한 특징(feature) 생성.

시간별 관측자료(temperature, humidity, wind_speed, pressure)로부터
- 과거 시차(lag) 기온
- 시각/계절의 주기성(sin/cos 인코딩)
을 특징으로 만든다. 라벨은 `horizon_hours`시간 뒤의 기온이다.
"""

import numpy as np
import pandas as pd

LAG_HOURS = [1, 3, 6, 12, 24]
BASE_COLS = ["temperature", "humidity", "wind_speed", "pressure"]

FEATURE_COLS = (
    [f"temp_lag_{lag}" for lag in LAG_HOURS]
    + ["humidity", "wind_speed", "pressure", "hour_sin", "hour_cos", "doy_sin", "doy_cos"]
)


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    """observed_at, temperature, humidity, wind_speed, pressure 컬럼을 갖는 df를
    받아 시간 grid로 재색인하고 lag/시각 특징을 추가한다."""
    data = df.sort_values("observed_at").drop_duplicates("observed_at").set_index("observed_at")

    full_index = pd.date_range(data.index.min(), data.index.max(), freq="h")
    data = data.reindex(full_index)
    data[BASE_COLS] = data[BASE_COLS].interpolate(limit=3)

    for lag in LAG_HOURS:
        data[f"temp_lag_{lag}"] = data["temperature"].shift(lag)

    hours = data.index.hour + data.index.minute / 60
    data["hour_sin"] = np.sin(2 * np.pi * hours / 24)
    data["hour_cos"] = np.cos(2 * np.pi * hours / 24)

    doy = data.index.dayofyear
    data["doy_sin"] = np.sin(2 * np.pi * doy / 365)
    data["doy_cos"] = np.cos(2 * np.pi * doy / 365)

    return data


def build_training_frame(df: pd.DataFrame, horizon_hours: int) -> tuple[pd.DataFrame, list[str]]:
    """학습용 (특징, 라벨) 프레임을 만든다. 결측 있는 행은 제거."""
    data = _add_features(df)
    data["target"] = data["temperature"].shift(-horizon_hours)
    data = data.dropna(subset=FEATURE_COLS + ["target"])
    return data, FEATURE_COLS


def build_latest_features(df: pd.DataFrame) -> pd.DataFrame | None:
    """가장 최근 시각 기준 예측 입력 특징 1행을 만든다. 라벨은 필요 없다."""
    data = _add_features(df)
    if data.empty:
        return None
    latest = data.iloc[[-1]]
    if latest[FEATURE_COLS].isna().any(axis=None):
        return None
    return latest[FEATURE_COLS]
