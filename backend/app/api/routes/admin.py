import hmac

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.prediction import UserPrediction
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    # ADMIN_TOKEN을 설정하지 않으면 이 API는 존재하지 않는 것처럼 동작한다.
    if not settings.admin_token:
        raise HTTPException(status_code=404, detail="Not Found")
    if not x_admin_token or not hmac.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(status_code=401, detail="관리자 토큰이 올바르지 않아요.")


@router.get("/reward-contacts", dependencies=[Depends(_require_admin)])
def reward_contacts(limit: int = 500, db: Session = Depends(get_db)):
    """보상 안내용으로 남긴 연락처 목록 (동의한 건만). 헤더 X-Admin-Token 필요."""
    rows = db.execute(
        select(UserPrediction, User.email)
        .outerjoin(User, User.id == UserPrediction.user_id)
        .where(
            UserPrediction.reward_contact.is_not(None),
            UserPrediction.contact_consent.is_(True),
        )
        .order_by(UserPrediction.created_at.desc())
        .limit(min(max(limit, 1), 2000))
    ).all()
    return [
        {
            "prediction_id": p.id,
            "created_at": p.created_at,
            "predict_date": p.predict_date,
            "station_id": p.station_id,
            "reward_contact": p.reward_contact,
            "account_email": email,
            "predicted_max_temp": p.predicted_max_temp,
            "predicted_sky_condition": p.predicted_sky_condition,
            "ai_predicted_max_temp": p.ai_predicted_max_temp,
        }
        for p, email in rows
    ]
