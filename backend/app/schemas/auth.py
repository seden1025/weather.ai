import re

from pydantic import BaseModel, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 128


def _normalize_email(v: str) -> str:
    v = v.strip().lower()
    if len(v) > 254 or not _EMAIL_RE.match(v):
        raise ValueError("이메일 형식이 올바르지 않아요.")
    return v


class SignupIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _normalize_email(v)

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        if not (MIN_PASSWORD_LEN <= len(v) <= MAX_PASSWORD_LEN):
            raise ValueError(
                f"비밀번호는 {MIN_PASSWORD_LEN}자 이상 {MAX_PASSWORD_LEN}자 이하로 입력해주세요."
            )
        return v


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return v.strip().lower()


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class AuthOut(BaseModel):
    token: str
    user: UserOut
