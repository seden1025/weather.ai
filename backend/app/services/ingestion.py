"""기상자료개방포털에서 받아온 관측자료를 DB에 저장한다."""

from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.models.observation import WeatherObservation
from app.services.kma_client import KmaClient

MAX_CHUNK_DAYS = 31  # kma_sfctm3.php 기간 조회 최대 범위


def _existing_keys(db: Session, station_ids: list[str], start: datetime, end: datetime) -> set:
    rows = db.execute(
        select(WeatherObservation.station_id, WeatherObservation.observed_at).where(
            WeatherObservation.station_id.in_(station_ids),
            WeatherObservation.observed_at >= start,
            WeatherObservation.observed_at <= end,
        )
    ).all()
    return {(r[0], r[1]) for r in rows}


def _insert_dataframe(db: Session, df: pd.DataFrame, existing: set) -> int:
    inserted = 0
    for _, row in df.iterrows():
        observed_at = row["observed_at"].to_pydatetime()
        key = (row["station_id"], observed_at)
        if key in existing:
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
        existing.add(key)
        inserted += 1
    db.commit()
    return inserted


async def ingest_recent(db: Session, station_id: str, hours: int = 24) -> int:
    """최근 `hours`시간 관측자료를 받아와 DB에 없는 것만 새로 저장한다 (단일 지점)."""
    end = now_kst()
    start = end - timedelta(hours=hours)

    client = KmaClient()
    df = await client.get_asos_hourly(station_id, start, end)
    existing = _existing_keys(db, [station_id], start, end)
    return _insert_dataframe(db, df, existing)


async def ingest_range(
    db: Session,
    station_ids: list[str],
    start: datetime,
    end: datetime,
    on_progress=None,
) -> int:
    """[start, end] 구간을 31일 단위로 나눠서 순차적으로 백필한다.

    station_ids에 여러 지점을 한 번에 넘기면, 기상청 API의 ':' 구분 다중 지점
    조회를 이용해 단일 지점 백필과 거의 같은 호출 수로 여러 지점을 동시에
    받아온다.

    on_progress(chunk_start, chunk_end, inserted_so_far)가 주어지면 청크마다 호출한다.
    """
    client = KmaClient()
    stn_param = ":".join(station_ids)
    existing = _existing_keys(db, station_ids, start, end)

    total_inserted = 0
    chunk_start = start
    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=MAX_CHUNK_DAYS), end)
        df = await client.get_asos_hourly(stn_param, chunk_start, chunk_end)
        total_inserted += _insert_dataframe(db, df, existing)
        if on_progress:
            on_progress(chunk_start, chunk_end, total_inserted)
        chunk_start = chunk_end

    return total_inserted
