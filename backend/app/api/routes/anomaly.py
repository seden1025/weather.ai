from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.anomaly import AnomalyEvent
from app.schemas.anomaly import AnomalyEventOut
from app.services.news_client import RssNewsClient

router = APIRouter(prefix="/anomaly", tags=["anomaly"])

INVESTIGATION_KEYWORDS = ["폭염", "한파", "폭우", "가뭄", "이상기후", "기상이변", "태풍", "폭설"]


@router.get("/events", response_model=list[AnomalyEventOut])
def list_events(station_id: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    stmt = select(AnomalyEvent).order_by(AnomalyEvent.observed_at.desc()).limit(limit)
    if station_id:
        stmt = stmt.where(AnomalyEvent.station_id == station_id)
    return db.execute(stmt).scalars().all()


@router.post("/events/{event_id}/investigate", response_model=AnomalyEventOut)
async def investigate_event(event_id: int, db: Session = Depends(get_db)):
    """이상치 이벤트에 대해 네이버 뉴스 검색으로 원인 후보 기사를 채워넣는다."""
    event = db.get(AnomalyEvent, event_id)
    if event is None:
        raise ValueError(f"AnomalyEvent {event_id} not found")

    news_client = RssNewsClient()
    items = await news_client.search(INVESTIGATION_KEYWORDS, around=event.observed_at)

    event.news_sources = [{"title": i["title"], "link": i["link"]} for i in items]
    event.news_summary = "; ".join(i["title"] for i in items[:5]) or None
    event.created_at = event.created_at or datetime.now(timezone.utc)

    db.commit()
    db.refresh(event)
    return event
