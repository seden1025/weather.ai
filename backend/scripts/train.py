"""기온 예측 XGBoost 모델 학습 스크립트.

사용법 (backend/ 디렉터리에서, venv 활성화 후):
    python -m scripts.train --station 108 --horizon 3
    python -m scripts.train --all --horizons 3,6,24   # 전국 지점 x 여러 horizon 일괄 학습

시간순으로 앞 85%를 학습, 뒤 15%를 테스트에 사용한다 (미래 데이터 유출 방지를
위해 랜덤 분할이 아닌 시간 기준 분할). 학습된 모델은
backend/app/ml/models/temp_h{horizon}_{station}.joblib 에 저장된다.
"""

import argparse
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sqlalchemy import select
from xgboost import XGBRegressor

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.ml.features import build_training_frame  # noqa: E402
from app.models.observation import WeatherObservation  # noqa: E402
from app.services.stations import STATIONS  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parent.parent / "app" / "ml" / "models"
MIN_ROWS = 200


def load_observations(station_id: str) -> pd.DataFrame:
    db = SessionLocal()
    try:
        rows = (
            db.execute(
                select(WeatherObservation).where(WeatherObservation.station_id == station_id)
            )
            .scalars()
            .all()
        )
    finally:
        db.close()
    return pd.DataFrame(
        [
            {
                "observed_at": r.observed_at,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "wind_speed": r.wind_speed,
                "pressure": r.pressure,
            }
            for r in rows
        ]
    )


def train_one(station_id: str, horizon_hours: int, raw: pd.DataFrame | None = None) -> float | None:
    """모델 하나를 학습해 저장하고, 테스트 MAE를 반환한다. 데이터 부족 시 None."""
    if raw is None:
        raw = load_observations(station_id)

    if len(raw) < MIN_ROWS:
        return None

    data, feature_cols = build_training_frame(raw, horizon_hours)
    if len(data) < MIN_ROWS:
        return None

    split_idx = int(len(data) * 0.85)
    train, test = data.iloc[:split_idx], data.iloc[split_idx:]
    if len(train) < 50 or len(test) < 10:
        return None

    model = XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05, n_jobs=-1)
    model.fit(train[feature_cols], train["target"])

    pred = model.predict(test[feature_cols])
    mae = mean_absolute_error(test["target"], pred)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"temp_h{horizon_hours}_{station_id}.joblib"
    joblib.dump(
        {"model": model, "feature_cols": feature_cols, "horizon_hours": horizon_hours, "mae": mae},
        model_path,
    )
    return mae


def main(station_ids: list[str], horizons: list[int]) -> None:
    for station_id in station_ids:
        raw = load_observations(station_id)
        print(f"[{station_id}] 관측 {len(raw)}건 로드")
        if len(raw) < MIN_ROWS:
            print(f"[{station_id}] 데이터가 너무 적어 건너뜀 (백필 먼저 필요)")
            continue

        for horizon_hours in horizons:
            baseline_mae = None
            data, feature_cols = build_training_frame(raw, horizon_hours)
            if len(data) >= MIN_ROWS:
                split_idx = int(len(data) * 0.85)
                test = data.iloc[split_idx:]
                baseline_mae = mean_absolute_error(test["target"], test["temperature"])

            mae = train_one(station_id, horizon_hours, raw=raw)
            if mae is None:
                print(f"[{station_id}] h={horizon_hours}: 샘플 부족으로 건너뜀")
                continue
            baseline_str = f", baseline={baseline_mae:.2f}°C" if baseline_mae is not None else ""
            print(f"[{station_id}] h={horizon_hours}: MAE={mae:.2f}°C{baseline_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--station", default=None)
    parser.add_argument("--all", action="store_true", help="stations.py의 전체 지점 학습")
    parser.add_argument("--horizon", type=int, default=None)
    parser.add_argument("--horizons", default="3,6,24", help="콤마로 구분 (기본: 3,6,24)")
    args = parser.parse_args()

    if args.all:
        ids = [s["id"] for s in STATIONS]
    elif args.station:
        ids = [args.station]
    else:
        ids = ["108"]

    horizons = [args.horizon] if args.horizon else [int(h) for h in args.horizons.split(",")]

    main(ids, horizons)
