from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, Integer, String, Text
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

    # 관찰: 지금 창밖은 어떤가
    sky_condition: Mapped[str] = mapped_column(String(16))  # 맑음/구름조금/흐림/비/눈
    wind_feel: Mapped[str] = mapped_column(String(16))  # 없음/약함/보통/강함
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 예측: 오늘 하루 전체는 어떨 것 같은가
    predicted_max_temp: Mapped[float] = mapped_column(Float)
    predicted_sky_condition: Mapped[str | None] = mapped_column(String(16), nullable=True)

    ai_predicted_max_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_predicted_sky_condition: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # 예측 근거: 어떤 단서를 바탕으로 그렇게 예측했는가 (선택지 + 직접 서술)
    prediction_basis: Mapped[list | None] = mapped_column(JSON, nullable=True)
    basis_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 로그인한 상태에서 제출했다면 계정 연결 (비로그인 제출도 허용)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # 보상 안내용 연락처(이메일 또는 전화번호). 비공개 - API 응답으로 내보내지 않는다.
    reward_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_consent: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False))
