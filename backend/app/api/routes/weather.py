from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.observation import WeatherObservation
from app.schemas.weather import ObservationOut

router = APIRouter(prefix="/weather", tags=["weather"])


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
def get_history(station_id: str, days: int = 7, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    stmt = (
        select(WeatherObservation)
        .where(
            WeatherObservation.station_id == station_id,
            WeatherObservation.observed_at >= since,
        )
        .order_by(WeatherObservation.observed_at.asc())
    )
    return db.execute(stmt).scalars().all()
