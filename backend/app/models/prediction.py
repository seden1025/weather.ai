from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserPrediction(Base):
    """사용자가 직접 관찰하고 예측한 '오늘의 최고기온' 기록.

    창밖을 보고 관찰한 내용(하늘 상태, 체감 바람)을 근거로 사람이 직접
    예측한 값과, 같은 시점 AI 모델의 예측값을 함께 저장해 나중에 실제
    관측값과 비교한다 (사람의 직관 vs AI 예측 비교가 이 프로젝트의 원래 질문).
    """

    __tablename__ = "user_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String(16), index=True)
    predict_date: Mapped[date] = mapped_column(Date, index=True)  # 예측 대상 날짜(KST)

    sky_condition: Mapped[str] = mapped_column(String(16))  # 맑음/구름조금/흐림/비/눈
    wind_feel: Mapped[str] = mapped_column(String(16))  # 없음/약함/보통/강함
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    predicted_max_temp: Mapped[float] = mapped_column(Float)
    ai_predicted_max_temp: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False))
