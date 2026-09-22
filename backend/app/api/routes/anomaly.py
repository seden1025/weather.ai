from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.anomaly import AnomalyEvent
from app.schemas.anomaly import AnomalyEventOut
from app.services.anomaly_investigation import investigate

router = APIRouter(prefix="/anomaly", tags=["anomaly"])


@router.get("/events", response_model=list[AnomalyEventOut])
def list_events(station_id: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(AnomalyEvent).order_by(AnomalyEvent.observed_at.desc()).limit(limit)
    if station_id:
        stmt = stmt.where(AnomalyEvent.station_id == station_id)
    return db.execute(stmt).scalars().all()


@router.post("/events/{event_id}/investigate", response_model=AnomalyEventOut)
async def investigate_event(event_id: int, db: Session = Depends(get_db)):
    """이상치 이벤트를 다시 조사해 뉴스 정보를 새로고침한다.

    이상치 탐지 시 자동으로 한 번 조사되지만, 이 엔드포인트로 수동 재조사도 가능하다.
    """
    event = db.get(AnomalyEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"AnomalyEvent {event_id} not found")
    return await investigate(db, event)
