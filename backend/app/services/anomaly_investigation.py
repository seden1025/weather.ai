"""이상치 이벤트에 대해 RSS 뉴스에서 원인 후보 기사를 찾아 채워넣는다."""

from sqlalchemy.orm import Session

from app.core.time import now_kst
from app.models.anomaly import AnomalyEvent
from app.services.news_client import RssNewsClient

INVESTIGATION_KEYWORDS = ["폭염", "한파", "폭우", "가뭄", "이상기후", "기상이변", "태풍", "폭설"]


async def investigate(db: Session, event: AnomalyEvent) -> AnomalyEvent:
    news_client = RssNewsClient()
    items = await news_client.search(INVESTIGATION_KEYWORDS, around=event.observed_at)

    event.news_sources = [{"title": i["title"], "link": i["link"]} for i in items]
    event.news_summary = "; ".join(i["title"] for i in items[:5]) or None
    event.created_at = event.created_at or now_kst()

    db.commit()
    db.refresh(event)
    return event
