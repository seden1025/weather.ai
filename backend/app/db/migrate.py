"""가벼운 스키마 보강.

Base.metadata.create_all()은 이미 존재하는 테이블에 새 컬럼을 추가해주지 않는다.
운영 DB에 이미 user_predictions 테이블이 있으므로, 시작할 때 빠진 컬럼만 ALTER TABLE로 채운다.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# (컬럼명, 타입 DDL). 모두 NULL 허용(또는 기본값 있음)이라 기존 행에 안전하다.
_NEW_PREDICTION_COLUMNS = [
    ("prediction_basis", "JSON"),
    ("basis_detail", "TEXT"),
    ("user_id", "INTEGER"),
    ("reward_contact", "VARCHAR(255)"),
    ("contact_consent", None),  # 기본값 문법이 DB마다 달라 아래에서 채운다
]


def ensure_prediction_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    if not inspector.has_table("user_predictions"):
        return  # create_all이 새로 만들 것이므로 할 일 없음

    existing = {c["name"] for c in inspector.get_columns("user_predictions")}
    is_sqlite = engine.dialect.name == "sqlite"
    bool_ddl = "BOOLEAN DEFAULT 0" if is_sqlite else "BOOLEAN DEFAULT FALSE"

    with engine.begin() as conn:
        for name, ddl in _NEW_PREDICTION_COLUMNS:
            if name in existing:
                continue
            conn.execute(
                text(f"ALTER TABLE user_predictions ADD COLUMN {name} {ddl or bool_ddl}")
            )
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_user_predictions_user_id "
                "ON user_predictions (user_id)"
            )
        )
