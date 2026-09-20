from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.db.session import get_db
from app.models.observation import WeatherObservation
from app.schemas.weather import ObservationOut
from app.services.ingestion import ingest_recent

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
