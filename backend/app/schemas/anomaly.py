from datetime import datetime

from pydantic import BaseModel


class AnomalyEventOut(BaseModel):
    id: int
    station_id: str
    variable: str
    observed_at: datetime
    value: float
    expected_low: float | None = None
    expected_high: float | None = None
    similar_past_event_ids: list | None = None
    news_summary: str | None = None
    news_sources: list | None = None
    created_at: datetime

    class Config:
        from_attributes = True
