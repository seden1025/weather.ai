"""학습된 XGBoost 모델로 기온/강수 여부를 예측한다."""

from pathlib import Path

import joblib
import pandas as pd

from app.ml.features import build_latest_features

MODEL_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"

_model_cache: dict[tuple[str, str, int], dict] = {}


def _load_model(kind: str, station_id: str, horizon_hours: int) -> dict | None:
    key = (kind, station_id, horizon_hours)
    if key in _model_cache:
        return _model_cache[key]

    path = MODEL_DIR / f"{kind}_h{horizon_hours}_{station_id}.joblib"
    if not path.exists():
        return None

    bundle = joblib.load(path)
    _model_cache[key] = bundle
    return bundle


def _available_horizons(kind: str, station_id: str) -> list[int]:
    if not MODEL_DIR.exists():
        return []
    prefix = f"{kind}_h"
    suffix = f"_{station_id}.joblib"
    horizons = []
    for path in MODEL_DIR.glob(f"{prefix}*{suffix}"):
        middle = path.name[len(prefix) : -len(suffix)]
        if middle.isdigit():
            horizons.append(int(middle))
    return sorted(horizons)


def available_horizons(station_id: str) -> list[int]:
    return _available_horizons("temp", station_id)


def predict_temperature(
    observations: pd.DataFrame, station_id: str, horizon_hours: int
) -> dict | None:
    bundle = _load_model("temp", station_id, horizon_hours)
    if bundle is None:
        return None

    features = build_latest_features(observations)
    if features is None:
        return None

    model = bundle["model"]
    predicted = float(model.predict(features[bundle["feature_cols"]])[0])
    return {
        "horizon_hours": horizon_hours,
        "predicted_temperature": round(predicted, 1),
        "model_test_mae": round(bundle.get("mae", 0.0), 2),
        "based_on": features.index[0].isoformat(),
    }


def predict_sky_condition(
    observations: pd.DataFrame, station_id: str, preferred_horizons: list[int] = (3, 6, 24)
) -> dict | None:
    """가장 정확도 높은(가까운) horizon의 강수 분류 모델로 오늘 날씨를 예측한다.

    맑음/비/눈 3가지만 구분한다 (구름량 데이터가 없어 흐림/구름조금은
    사람이 직접 관찰해서 판단해야 하는 영역으로 남겨둔다).
    """
    for horizon_hours in preferred_horizons:
        bundle = _load_model("rain", station_id, horizon_hours)
        if bundle is None:
            continue

        features = build_latest_features(observations)
        if features is None:
            return None

        model = bundle["model"]
        rain_prob = float(model.predict_proba(features[bundle["feature_cols"]])[0][1])

        temp_result = predict_temperature(observations, station_id, horizon_hours)
        predicted_temp = temp_result["predicted_temperature"] if temp_result else None

        will_rain = rain_prob >= 0.5
        if will_rain:
            condition = "눈" if (predicted_temp is not None and predicted_temp <= 1.0) else "비"
        else:
            condition = "맑음"

        return {
            "horizon_hours": horizon_hours,
            "condition": condition,
            "rain_probability": round(rain_prob, 2),
            "model_accuracy": round(bundle.get("accuracy", 0.0), 2),
        }

    return None
