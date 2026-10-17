from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User


def _user_from_header(authorization: str | None, db: Session) -> User | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    user_id = decode_token(token.strip())
    if user_id is None:
        return None
    return db.get(User, user_id)


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """로그인하지 않았거나 토큰이 만료/위조된 경우 None (비로그인 사용도 허용하는 곳에서 사용)."""
    return _user_from_header(authorization, db)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    user = _user_from_header(authorization, db)
    if user is None:
        raise HTTPException(status_code=401, detail="로그인이 필요해요.")
    return user
