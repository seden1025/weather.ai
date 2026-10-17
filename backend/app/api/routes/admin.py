import hmac
from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.predictions import _actual_max_temp, _actual_rained
from app.core.config import settings
from app.core.time import now_kst
from app.db.session import get_db
from app.models.prediction import UserPrediction
from app.models.user import User
from app.services.export import XLSX_MEDIA_TYPE, actual_sky, build_workbook

# 한 번에 내보낼 수 있는 최대 응답 수 (무료 서버가 한 요청에 너무 오래 걸리지 않도록)
EXPORT_MAX_ROWS = 20000

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


@router.get("/export/predictions.xlsx", dependencies=[Depends(_require_admin)])
def export_predictions(
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    """설문(예측) 응답 전체를 엑셀 파일로 내려준다. 헤더 X-Admin-Token 필요.

    start/end(YYYY-MM-DD)를 주면 예측 날짜 기준으로 그 기간만 포함한다.
    보상 연락처는 수집·이용에 동의한 응답에서만 채워진다.
    """
    query = select(UserPrediction, User.email).outerjoin(User, User.id == UserPrediction.user_id)
    if start:
        query = query.where(UserPrediction.predict_date >= start)
    if end:
        query = query.where(UserPrediction.predict_date <= end)
    found = db.execute(
        query.order_by(UserPrediction.created_at.asc()).limit(EXPORT_MAX_ROWS)
    ).all()

    # 같은 지점·날짜의 실제 관측값은 한 번만 조회한다.
    actuals: dict[tuple[str, date], tuple[float | None, bool | None]] = {}

    def actual_for(station_id: str, day: date):
        key = (station_id, day)
        if key not in actuals:
            actuals[key] = (
                _actual_max_temp(db, station_id, day),
                _actual_rained(db, station_id, day),
            )
        return actuals[key]

    rows = []
    for p, email in found:
        actual_temp, rained = actual_for(p.station_id, p.predict_date)
        rows.append(
            {
                "id": p.id,
                "created_at": p.created_at,
                "predict_date": p.predict_date,
                "station_id": p.station_id,
                "account_email": email,
                "observed_sky": p.sky_condition,
                "observed_wind": p.wind_feel,
                "user_sky": p.predicted_sky_condition,
                "user_temp": p.predicted_max_temp,
                "basis": ", ".join(p.prediction_basis or []),
                "basis_detail": p.basis_detail,
                "memo": p.memo,
                "ai_sky": p.ai_predicted_sky_condition,
                "ai_temp": p.ai_predicted_max_temp,
                "actual_temp": actual_temp,
                "actual_sky": actual_sky(rained, actual_temp),
                "reward_contact": p.reward_contact if p.contact_consent else None,
                "contact_consent": bool(p.contact_consent and p.reward_contact),
            }
        )

    filename = f"weather-ai-responses-{now_kst():%Y%m%d-%H%M}.xlsx"
    return Response(
        content=build_workbook(rows),
        media_type=XLSX_MEDIA_TYPE,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )
