"""비밀번호 해시와 로그인 토큰 (표준 라이브러리만 사용, 추가 패키지 불필요)."""

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import settings

# AUTH_SECRET이 설정되지 않으면 프로세스마다 임시 키를 만든다.
# 이 경우 서버가 재시작(무료 호스팅의 잠들기 포함)될 때마다 모든 로그인이 풀리므로
# 운영에서는 반드시 AUTH_SECRET을 환경변수로 지정해야 한다.
_SECRET = (settings.auth_secret or secrets.token_urlsafe(48)).encode()

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P
    )
    return f"scrypt${_b64e(salt)}${_b64e(digest)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = _b64d(digest_b64)
        actual = hashlib.scrypt(
            password.encode(),
            salt=_b64d(salt_b64),
            n=_SCRYPT_N,
            r=_SCRYPT_R,
            p=_SCRYPT_P,
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected)


# 존재하지 않는 이메일로 로그인을 시도해도 응답 시간이 비슷하도록 쓰는 더미 해시
DUMMY_HASH = hash_password("dummy-password-for-timing")


def create_token(user_id: int) -> str:
    payload = {"sub": user_id, "exp": int(time.time()) + settings.token_ttl_days * 86400}
    body = _b64e(json.dumps(payload, separators=(",", ":")).encode())
    sig = _b64e(hmac.new(_SECRET, body.encode(), hashlib.sha256).digest())
    return f"{body}.{sig}"


def decode_token(token: str) -> int | None:
    """유효한 토큰이면 user_id, 아니면 None."""
    try:
        body, sig = token.split(".")
        expected = _b64e(hmac.new(_SECRET, body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(body))
        if int(payload["exp"]) < time.time():
            return None
        return int(payload["sub"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None
