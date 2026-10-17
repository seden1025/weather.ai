from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import (
    DUMMY_HASH,
    create_token,
    hash_password,
    verify_password,
)
from app.core.time import now_kst
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AuthOut, LoginIn, SignupIn, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthOut, status_code=201)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.execute(select(User.id).where(User.email == body.email)).first():
        raise HTTPException(status_code=409, detail="이미 가입된 이메일이에요. 로그인해주세요.")

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        created_at=now_kst(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # 동시에 같은 이메일로 가입 요청이 겹친 경우
        db.rollback()
        raise HTTPException(status_code=409, detail="이미 가입된 이메일이에요. 로그인해주세요.")
    db.refresh(user)
    return AuthOut(token=create_token(user.id), user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()
    # 이메일 존재 여부와 상관없이 같은 오류/비슷한 처리 시간을 보여 계정 유무를 추측하기 어렵게 한다.
    stored = user.password_hash if user else DUMMY_HASH
    ok = verify_password(body.password, stored)
    if not user or not ok:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않아요.")
    return AuthOut(token=create_token(user.id), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
