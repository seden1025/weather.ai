"""기상자료개방포털에서 받아온 관측자료를 DB에 저장한다."""

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.models.observation import WeatherObservation
from app.services.kma_client import KmaClient


async def ingest_recent(db: Session, station_id: str, hours: int = 24) -> int:
    """최근 `hours`시간 관측자료를 받아와 DB에 없는 것만 새로 저장한다."""
    end = now_kst()
    start = end - timedelta(hours=hours)

    client = KmaClient()
    df = await client.get_asos_hourly(station_id, start, end)

    inserted = 0
    for _, row in df.iterrows():
        observed_at = row["observed_at"].to_pydatetime()
        exists = db.execute(
            select(WeatherObservation.id).where(
                WeatherObservation.station_id == row["station_id"],
                WeatherObservation.observed_at == observed_at,
            )
        ).scalar_one_or_none()
        if exists:
            continue
        db.add(
            WeatherObservation(
                station_id=row["station_id"],
                observed_at=observed_at,
                temperature=row["temperature"],
                precipitation=row["precipitation"],
                wind_speed=row["wind_speed"],
                humidity=row["humidity"],
                pressure=row["pressure"],
            )
        )
        inserted += 1

    db.commit()
    return inserted
