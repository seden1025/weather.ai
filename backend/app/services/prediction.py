"""학습된 XGBoost 모델로 기온을 예측한다."""

from pathlib import Path

import joblib
import pandas as pd

from app.ml.features import build_latest_features

MODEL_DIR = Path(__file__).resolve().parent.parent / "ml" / "models"

_model_cache: dict[tuple[str, int], dict] = {}


def _load_model(station_id: str, horizon_hours: int) -> dict | None:
    key = (station_id, horizon_hours)
    if key in _model_cache:
        return _model_cache[key]

    path = MODEL_DIR / f"temp_h{horizon_hours}_{station_id}.joblib"
    if not path.exists():
        return None

    bundle = joblib.load(path)
    _model_cache[key] = bundle
    return bundle


def available_horizons(station_id: str) -> list[int]:
    if not MODEL_DIR.exists():
        return []
    prefix = "temp_h"
    suffix = f"_{station_id}.joblib"
    horizons = []
    for path in MODEL_DIR.glob(f"{prefix}*{suffix}"):
        middle = path.name[len(prefix) : -len(suffix)]
        if middle.isdigit():
            horizons.append(int(middle))
    return sorted(horizons)


def predict_temperature(
    observations: pd.DataFrame, station_id: str, horizon_hours: int
) -> dict | None:
    bundle = _load_model(station_id, horizon_hours)
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
