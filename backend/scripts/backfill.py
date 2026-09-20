"""과거 관측자료 백필 스크립트.

사용법 (backend/ 디렉터리에서, venv 활성화 후):
    python -m scripts.backfill --station 108 --years 5

DATABASE_URL 환경변수(.env)가 가리키는 DB에 그대로 적재된다. 로컬 SQLite로
테스트한 뒤, 운영 DB(Neon)에 반영하려면 backend/.env의 DATABASE_URL을
잠깐 Neon 연결 문자열로 바꾸고 실행하면 된다.
"""

import argparse
import asyncio
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.time import now_kst  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.services.ingestion import ingest_range  # noqa: E402


async def main(station_id: str, years: float) -> None:
    Base.metadata.create_all(bind=engine)

    end = now_kst()
    start = end - timedelta(days=int(years * 365))

    def report(chunk_start, chunk_end, total_inserted):
        print(f"  {chunk_start.date()} ~ {chunk_end.date()}  (누적 {total_inserted}건)")

    db = SessionLocal()
    try:
        print(f"지점 {station_id}: {start.date()} ~ {end.date()} 백필 시작")
        total = await ingest_range(db, station_id, start, end, on_progress=report)
        print(f"완료: 새로 저장된 행 {total}건")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--station", default="108", help="지점번호 (기본: 108 서울)")
    parser.add_argument("--years", type=float, default=5, help="과거 몇 년치 (기본: 5)")
    args = parser.parse_args()
    asyncio.run(main(args.station, args.years))
