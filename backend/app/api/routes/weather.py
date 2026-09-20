from datetime import timedelta

import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.db.session import get_db
from app.models.observation import WeatherObservation
from app.schemas.weather import ObservationOut
from app.services.ingestion import ingest_recent
from app.services.prediction import available_horizons, predict_temperature

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("/ingest/{station_id}")
async def ingest(station_id: str, hours: int = 24, db: Session = Depends(get_db)):
    """기상자료개방포털에서 최근 관측자료를 받아와 DB에 저장한다."""
    inserted = await ingest_recent(db, station_id, hours)
    return {"inserted": inserted}


@router.get("/current/{station_id}", response_model=ObservationOut | None)
def get_current(station_id: str, db: Session = Depends(get_db)):
    stmt = (
        select(WeatherObservation)
        .where(WeatherObservation.station_id == station_id)
        .order_by(WeatherObservation.observed_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


@router.get("/history/{station_id}", response_model=list[ObservationOut])
def get_history(
    station_id: str, hours: int | None = None, days: int = 7, db: Session = Depends(get_db)
):
    # observed_at은 기상청 응답 기준 KST 시각(naive)으로 저장되어 있다.
    now = now_kst()
    since = now - timedelta(hours=hours) if hours is not None else now - timedelta(days=days)
    stmt = (
        select(WeatherObservation)
        .where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= since,
        )
        .order_by(WeatherObservation.observed_at.asc())
    )
    return db.execute(stmt).scalars().all()


@router.get("/forecast/{station_id}")
def get_forecast(station_id: str, db: Session = Depends(get_db)):
    """학습된 모델로 기온을 예측한다 (사용 가능한 모든 horizon에 대해)."""
    horizons = available_horizons(station_id)
    if not horizons:
        return []

    since = now_kst() - timedelta(hours=48)
    stmt = (
        select(WeatherObservation)
        .where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= since,
        )
        .order_by(WeatherObservation.observed_at.asc())
    )
    rows = db.execute(stmt).scalars().all()
    if not rows:
        return []

    df = pd.DataFrame(
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

    predictions = [predict_temperature(df, station_id, h) for h in horizons]
    return [p for p in predictions if p is not None]
