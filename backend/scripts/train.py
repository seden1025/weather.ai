"""기온 예측 XGBoost 모델 학습 스크립트.

사용법 (backend/ 디렉터리에서, venv 활성화 후):
    python -m scripts.train --station 108 --horizon 3

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

MODEL_DIR = Path(__file__).resolve().parent.parent / "app" / "ml" / "models"


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


def main(station_id: str, horizon_hours: int) -> None:
    raw = load_observations(station_id)
    print(f"관측 {len(raw)}건 로드")
    if len(raw) < 200:
        print("데이터가 너무 적습니다. 백필을 먼저 실행하세요.")
        return

    data, feature_cols = build_training_frame(raw, horizon_hours)
    print(f"학습 가능 샘플 {len(data)}건 (lag/결측 제거 후)")

    split_idx = int(len(data) * 0.85)
    train, test = data.iloc[:split_idx], data.iloc[split_idx:]

    model = XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.05, n_jobs=-1)
    model.fit(train[feature_cols], train["target"])

    pred = model.predict(test[feature_cols])
    mae = mean_absolute_error(test["target"], pred)
    baseline_mae = mean_absolute_error(test["target"], test["temperature"])  # "지금과 같다" 예측
    print(f"테스트 MAE: {mae:.2f}°C  (단순 지속성 예측 baseline: {baseline_mae:.2f}°C, n_test={len(test)})")

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"temp_h{horizon_hours}_{station_id}.joblib"
    joblib.dump(
        {"model": model, "feature_cols": feature_cols, "horizon_hours": horizon_hours, "mae": mae},
        model_path,
    )
    print(f"모델 저장: {model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--station", default="108")
    parser.add_argument("--horizon", type=int, default=3)
    args = parser.parse_args()
    main(args.station, args.horizon)
