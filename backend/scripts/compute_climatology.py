"""지점 x 변수 x 월별 평년 평균/표준편차를 계산해 climatology.json으로 저장한다.

로컬에 백필된 5년치 데이터를 이용해 한 번만 계산해두면, 운영 DB(최근 데이터만
보관)에서도 이 파일만으로 "평년과 얼마나 다른지"를 즉시 계산할 수 있다.

사용법 (backend/ 디렉터리에서, venv 활성화 후):
    python -m scripts.compute_climatology
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.db.session import SessionLocal  # noqa: E402
from app.models.observation import WeatherObservation  # noqa: E402
from app.services.stations import STATIONS  # noqa: E402

OUT_PATH = Path(__file__).resolve().parent.parent / "app" / "services" / "climatology.json"
VARIABLES = ["temperature", "humidity", "wind_speed", "pressure"]
MIN_SAMPLES = 30  # 이보다 표본이 적은 지점/월/변수는 신뢰도가 낮아 제외


def main() -> None:
    db = SessionLocal()
    stats: dict[str, dict[str, float]] = {}
    try:
        for s in STATIONS:
            station_id = s["id"]
            rows = db.execute(
                select(
                    WeatherObservation.observed_at,
                    WeatherObservation.temperature,
                    WeatherObservation.humidity,
                    WeatherObservation.wind_speed,
                    WeatherObservation.pressure,
                ).where(WeatherObservation.station_id == station_id)
            ).all()
            if not rows:
                print(f"[{station_id}] 데이터 없음, 건너뜀")
                continue

            df = pd.DataFrame(
                rows, columns=["observed_at", "temperature", "humidity", "wind_speed", "pressure"]
            )
            df["month"] = pd.to_datetime(df["observed_at"]).dt.month

            count = 0
            for var in VARIABLES:
                grouped = df.dropna(subset=[var]).groupby("month")[var].agg(["mean", "std", "count"])
                for month, row in grouped.iterrows():
                    if row["count"] < MIN_SAMPLES or not row["std"]:
                        continue
                    key = f"{station_id}:{var}:{int(month)}"
                    stats[key] = {"mean": round(float(row["mean"]), 3), "std": round(float(row["std"]), 3)}
                    count += 1
            print(f"[{station_id}] {count}개 항목")
    finally:
        db.close()

    OUT_PATH.write_text(json.dumps(stats, ensure_ascii=False), encoding="utf-8")
    print(f"완료: {len(stats)}개 항목 저장 -> {OUT_PATH}")


if __name__ == "__main__":
    main()
