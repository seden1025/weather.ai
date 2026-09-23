"""강수 여부(비/눈) 예측 XGBoost 분류 모델 학습 스크립트.

사용법 (backend/ 디렉터리에서, venv 활성화 후):
    python -m scripts.train_rain --station 108 --horizon 3
    python -m scripts.train_rain --all --horizons 3,6,24

기온 모델(scripts/train.py)과 같은 시간 기준 분할을 쓴다. 학습된 모델은
backend/app/ml/models/rain_h{horizon}_{station}.joblib 에 저장된다.
"""

import argparse
import sys
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, f1_score
from xgboost import XGBClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ml.features import build_rain_training_frame  # noqa: E402
from app.services.stations import STATIONS  # noqa: E402
from scripts.train import MIN_ROWS, load_observations  # noqa: E402

MODEL_DIR = Path(__file__).resolve().parent.parent / "app" / "ml" / "models"


def train_one_rain(station_id: str, horizon_hours: int, raw=None) -> dict | None:
    if raw is None:
        raw = load_observations(station_id)
    if len(raw) < MIN_ROWS:
        return None

    data, feature_cols = build_rain_training_frame(raw, horizon_hours)
    if len(data) < MIN_ROWS or data["target"].nunique() < 2:
        return None

    split_idx = int(len(data) * 0.85)
    train, test = data.iloc[:split_idx], data.iloc[split_idx:]
    if len(train) < 50 or len(test) < 10 or train["target"].nunique() < 2:
        return None

    positive = max(train["target"].sum(), 1)
    negative = len(train) - positive
    scale_pos_weight = negative / positive  # 비 오는 시간이 훨씬 적어서 가중치로 보정

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        n_jobs=-1,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight,
    )
    model.fit(train[feature_cols], train["target"])

    pred = model.predict(test[feature_cols])
    acc = accuracy_score(test["target"], pred)
    f1 = f1_score(test["target"], pred, zero_division=0)
    rain_rate = float(test["target"].mean())

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"rain_h{horizon_hours}_{station_id}.joblib"
    joblib.dump(
        {
            "model": model,
            "feature_cols": feature_cols,
            "horizon_hours": horizon_hours,
            "accuracy": acc,
            "f1": f1,
            "rain_rate": rain_rate,
        },
        model_path,
    )
    return {"accuracy": acc, "f1": f1, "rain_rate": rain_rate}


def main(station_ids: list[str], horizons: list[int]) -> None:
    for station_id in station_ids:
        raw = load_observations(station_id)
        if len(raw) < MIN_ROWS:
            print(f"[{station_id}] 데이터가 너무 적어 건너뜀")
            continue
        for horizon_hours in horizons:
            result = train_one_rain(station_id, horizon_hours, raw=raw)
            if result is None:
                print(f"[{station_id}] h={horizon_hours}: 샘플/클래스 부족으로 건너뜀")
                continue
            print(
                f"[{station_id}] h={horizon_hours}: "
                f"acc={result['accuracy']:.2f} f1={result['f1']:.2f} "
                f"(강수 비율 {result['rain_rate']:.2%})"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--station", default=None)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--horizon", type=int, default=None)
    parser.add_argument("--horizons", default="3,6,24")
    args = parser.parse_args()

    if args.all:
        ids = [s["id"] for s in STATIONS]
    elif args.station:
        ids = [args.station]
    else:
        ids = ["108"]

    horizons = [args.horizon] if args.horizon else [int(h) for h in args.horizons.split(",")]
    main(ids, horizons)
