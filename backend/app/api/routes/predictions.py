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
from app.services.prediction import predict_sky_condition, predict_temperature

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


def _actual_rained(db: Session, station_id: str, predict_date) -> bool | None:
    start = datetime.combine(predict_date, datetime.min.time())
    end = start + timedelta(days=1)
    # 관측치가 없으면(하루가 아직 안 지났거나 데이터 없음) None, 있으면 결측 강수량은
    # 0(비 안 옴)으로 취급한다 - KMA는 무강수 시간을 결측으로 내려보내기 때문.
    row = db.execute(
        select(
            func.count(WeatherObservation.id),
            func.max(func.coalesce(WeatherObservation.precipitation, 0)),
        ).where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= start,
            WeatherObservation.observed_at < end,
        )
    ).one()
    count, max_precip = row
    if not count:
        return None
    return max_precip > 0.1


def _to_out(db: Session, p: UserPrediction) -> PredictionOut:
    return PredictionOut(
        id=p.id,
        station_id=p.station_id,
        predict_date=p.predict_date,
        sky_condition=p.sky_condition,
        wind_feel=p.wind_feel,
        memo=p.memo,
        predicted_max_temp=p.predicted_max_temp,
        predicted_sky_condition=p.predicted_sky_condition,
        ai_predicted_max_temp=p.ai_predicted_max_temp,
        ai_predicted_sky_condition=p.ai_predicted_sky_condition,
        actual_max_temp=_actual_max_temp(db, p.station_id, p.predict_date),
        actual_rained=_actual_rained(db, p.station_id, p.predict_date),
        created_at=p.created_at,
    )


def _recent_observations_df(db: Session, station_id: str) -> pd.DataFrame | None:
    recent = (
        db.execute(
            select(WeatherObservation)
            .where(
                WeatherObservation.station_id == station_id,
                WeatherObservation.observed_at >= now_kst() - timedelta(hours=48),
            )
            .order_by(WeatherObservation.observed_at.asc())
        )
        .scalars()
        .all()
    )
    if not recent:
        return None
    return pd.DataFrame(
        [
            {
                "observed_at": r.observed_at,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "wind_speed": r.wind_speed,
                "pressure": r.pressure,
                "precipitation": r.precipitation,
            }
            for r in recent
        ]
    )


@router.post("/{station_id}", response_model=PredictionOut)
def create_prediction(station_id: str, body: PredictionIn, db: Session = Depends(get_db)):
    """관찰 기반 오늘의 최고기온·날씨 예측을 저장한다. 같은 시점 AI 예측값도 함께 기록한다."""
    today = now_kst().date()
    df = _recent_observations_df(db, station_id)

    ai_temp = None
    if df is not None:
        for horizon in (24, 6, 3):
            result = predict_temperature(df, station_id, horizon)
            if result:
                ai_temp = result["predicted_temperature"]
                break

    ai_sky = None
    if df is not None:
        sky_result = predict_sky_condition(df, station_id)
        if sky_result:
            ai_sky = sky_result["condition"]

    prediction = UserPrediction(
        station_id=station_id,
        predict_date=today,
        sky_condition=body.sky_condition,
        wind_feel=body.wind_feel,
        memo=body.memo,
        predicted_max_temp=body.predicted_max_temp,
        predicted_sky_condition=body.predicted_sky_condition,
        ai_predicted_max_temp=ai_temp,
        ai_predicted_sky_condition=ai_sky,
        created_at=now_kst(),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return _to_out(db, prediction)


@router.get("/{station_id}", response_model=list[PredictionOut])
def list_predictions(station_id: str, limit: int = 20, db: Session = Depends(get_db)):
    predictions = (
        db.execute(
            select(UserPrediction)
            .where(UserPrediction.station_id == station_id)
            .order_by(UserPrediction.created_at.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    return [_to_out(db, p) for p in predictions]
