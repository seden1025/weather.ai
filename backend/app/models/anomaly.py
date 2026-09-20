from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AnomalyEvent(Base):
    """탐지된 이상치와 그 원인 조사 결과를 누적 저장하는 전용 테이블."""

    __tablename__ = "anomaly_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(16), index=True)
    variable: Mapped[str] = mapped_column(String(32))  # 예: temperature, precipitation
    # 항상 한국시간(KST) wall-clock 기준 naive datetime으로 저장
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), index=True)
    value: Mapped[float] = mapped_column(Float)
    expected_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    expected_high: Mapped[float | None] = mapped_column(Float, nullable=True)

    # 과거 유사 이상치 사례의 observation id 목록
    similar_past_event_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)

    news_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    news_sources: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False))
