from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.db.session import get_db
from app.models.observation import WeatherObservation
from app.models.prediction import UserPrediction
from app.schemas.prediction import PredictionIn, PredictionOut
from app.services.prediction import predict_temperature

router = APIRouter(prefix="/predictions", tags=["predictions"])


def _actual_max_temp(db: Session, station_id: str, predict_date) -> float | None:
    start = datetime.combine(predict_date, datetime.min.time())
    end = start + timedelta(days=1)
    return db.execute(
        select(func.max(WeatherObservation.temperature)).where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= start,
            WeatherObservation.observed_at < end,
        )
    ).scalar()


def _to_out(db: Session, p: UserPrediction) -> PredictionOut:
    return PredictionOut(
        id=p.id,
        station_id=p.station_id,
        predict_date=p.predict_date,
        sky_condition=p.sky_condition,
        wind_feel=p.wind_feel,
        memo=p.memo,
        predicted_max_temp=p.predicted_max_temp,
        ai_predicted_max_temp=p.ai_predicted_max_temp,
        actual_max_temp=_actual_max_temp(db, p.station_id, p.predict_date),
        created_at=p.created_at,
    )


@router.post("/{station_id}", response_model=PredictionOut)
def create_prediction(station_id: str, body: PredictionIn, db: Session = Depends(get_db)):
    """관찰 기반 오늘의 최고기온 예측을 저장한다. 같은 시점 AI 예측값도 함께 기록한다."""
    today = now_kst().date()

    # 오늘 남은 시간 중 가장 먼 horizon을 "AI의 오늘 최고기온 예측"으로 사용한다.
    recent = db.execute(
        select(WeatherObservation)
        .where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= now_kst() - timedelta(hours=48),
        )
        .order_by(WeatherObservation.observed_at.asc())
    ).scalars().all()

    ai_temp = None
    if recent:
        df = pd.DataFrame(
            [
                {
                    "observed_at": r.observed_at,
                    "temperature": r.temperature,
                    "humidity": r.humidity,
                    "wind_speed": r.wind_speed,
                    "pressure": r.pressure,
                }
                for r in recent
            ]
        )
        for horizon in (24, 6, 3):
            result = predict_temperature(df, station_id, horizon)
            if result:
                ai_temp = result["predicted_temperature"]
                break

    prediction = UserPrediction(
        station_id=station_id,
        predict_date=today,
        sky_condition=body.sky_condition,
        wind_feel=body.wind_feel,
        memo=body.memo,
        predicted_max_temp=body.predicted_max_temp,
        ai_predicted_max_temp=ai_temp,
        created_at=now_kst(),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return _to_out(db, prediction)


@router.get("/{station_id}", response_model=list[PredictionOut])
def list_predictions(station_id: str, limit: int = 20, db: Session = Depends(get_db)):
    predictions = db.execute(
        select(UserPrediction)
        .where(UserPrediction.station_id == station_id)
        .order_by(UserPrediction.created_at.desc())
        .limit(limit)
    ).scalars().all()
    return [_to_out(db, p) for p in predictions]
