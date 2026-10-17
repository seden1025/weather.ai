import re
from datetime import date, datetime

from pydantic import BaseModel, field_validator, model_validator

# 예측 근거 선택지. 프론트엔드(frontend/app/predict/page.tsx)의 BASIS_OPTIONS와 같아야 한다.
BASIS_OPTIONS = (
    "지금 하늘·구름 모습",
    "바람의 세기·방향",
    "지금 기온·체감 온도",
    "습도·공기의 느낌",
    "어제·최근 며칠의 날씨",
    "일기예보·날씨 앱",
    "계절·평소 경험",
    "그냥 직감",
    "기타",
)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MAX_TEXT = 500


def normalize_contact(raw: str | None) -> str | None:
    """보상 안내용 연락처를 이메일(소문자) 또는 숫자만 남긴 전화번호로 정규화한다."""
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    if "@" in s:
        if len(s) > 254 or not _EMAIL_RE.match(s):
            raise ValueError("이메일 형식이 올바르지 않아요.")
        return s.lower()
    digits = re.sub(r"[\s\-()]", "", s)
    if digits.startswith("+82"):
        digits = "0" + digits[3:]
    if not re.fullmatch(r"\d{9,11}", digits):
        raise ValueError("전화번호는 숫자 9~11자리로 입력해주세요. (예: 010-1234-5678)")
    return digits


class PredictionIn(BaseModel):
    sky_condition: str
    wind_feel: str
    predicted_max_temp: float
    predicted_sky_condition: str | None = None
    memo: str | None = None

    # 예측 근거
    prediction_basis: list[str] = []
    basis_detail: str | None = None

    # 보상 안내용 연락처 (선택). 남기려면 수집·이용 동의가 필요하다.
    reward_contact: str | None = None
    contact_consent: bool = False

    @field_validator("prediction_basis")
    @classmethod
    def _check_basis(cls, v: list[str]) -> list[str]:
        unique = list(dict.fromkeys(v))
        invalid = [x for x in unique if x not in BASIS_OPTIONS]
        if invalid:
            raise ValueError("알 수 없는 예측 근거 항목이 포함되어 있어요.")
        return unique

    @field_validator("memo", "basis_detail")
    @classmethod
    def _clean_text(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if len(v) > _MAX_TEXT:
            raise ValueError(f"글자 수는 {_MAX_TEXT}자 이하로 입력해주세요.")
        return v or None

    @field_validator("reward_contact")
    @classmethod
    def _check_contact(cls, v: str | None) -> str | None:
        return normalize_contact(v)

    @model_validator(mode="after")
    def _require_consent(self):
        if self.reward_contact and not self.contact_consent:
            raise ValueError("연락처를 남기려면 개인정보 수집·이용에 동의해주세요.")
        return self


class PredictionOut(BaseModel):
    id: int
    station_id: str
    predict_date: date
    sky_condition: str
    wind_feel: str
    memo: str | None = None
    predicted_max_temp: float
    predicted_sky_condition: str | None = None
    prediction_basis: list[str] | None = None
    basis_detail: str | None = None
    # 연락처 값 자체는 공개하지 않고, 등록 여부만 알려준다.
    reward_contact_registered: bool = False
    ai_predicted_max_temp: float | None = None
    ai_predicted_sky_condition: str | None = None
    actual_max_temp: float | None = None
    actual_rained: bool | None = None
    created_at: datetime

    class Config:
        from_attributes = True
