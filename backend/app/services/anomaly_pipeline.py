"""신규 관측치가 들어올 때마다 자동으로 이상치를 탐지하고, 곧바로 뉴스까지
조사해서 저장한다 (ingest_recent에서 호출됨 - 실시간/최근 데이터 경로에만
연결하고, 수년치를 한 번에 넣는 backfill에는 연결하지 않는다. 과거 데이터는
RSS로 원인을 찾을 수 없고, 매 건마다 조사하면 낭비이기 때문)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.models.anomaly import AnomalyEvent
from app.models.observation import WeatherObservation
from app.services.anomaly_detection import check_anomaly
from app.services.anomaly_investigation import investigate

CHECKED_VARIABLES = ["temperature"]


async def detect_and_investigate(db: Session, rows: list[WeatherObservation]) -> list[AnomalyEvent]:
    created: list[AnomalyEvent] = []

    for row in rows:
        month = row.observed_at.month
        for variable in CHECKED_VARIABLES:
            value = getattr(row, variable)
            if value is None:
                continue

            result = check_anomaly(row.station_id, variable, month, value)
            if result is None:
                continue

            exists = db.execute(
                select(AnomalyEvent.id).where(
                    AnomalyEvent.station_id == row.station_id,
                    AnomalyEvent.variable == variable,
                    AnomalyEvent.observed_at == row.observed_at,
                )
            ).scalar_one_or_none()
            if exists:
                continue

            event = AnomalyEvent(
                station_id=row.station_id,
                variable=variable,
                observed_at=row.observed_at,
                value=value,
                expected_low=result["expected_low"],
                expected_high=result["expected_high"],
                created_at=now_kst(),
            )
            db.add(event)
            db.commit()
            db.refresh(event)

            await investigate(db, event)
            created.append(event)

    return created
