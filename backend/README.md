# Weather AI Backend (FastAPI)

## 설치

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env
```

`.env`에 `KMA_API_KEY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`, `DATABASE_URL`을 채운다.

## 실행

```bash
uvicorn app.main:app --reload
```

http://localhost:8000/docs 에서 API 문서 확인.

## 폴더 구조

```
app/
  core/config.py       환경변수 설정
  db/                   SQLAlchemy 세션/베이스
  models/               ORM 모델 (관측자료, 이상치)
  schemas/              Pydantic 응답 스키마
  services/
    kma_client.py       기상자료개방포털 API 연동
    news_client.py       네이버 뉴스 검색 API 연동
    anomaly_detection.py 이상치 탐지 + 유사사례 검색 로직
  api/routes/           FastAPI 라우터
main.py                 앱 엔트리포인트
```

## 참고

- `kma_client.py`의 응답 파싱은 실제 발급받은 데이터셋(ASOS 시간자료 등) 스펙에
  맞춰 조정이 필요합니다. 포털에서 "Open API 상세설명"의 응답 예시를 확인하세요.
- DB는 PostgreSQL을 기본으로 하며, 시계열 데이터가 많아지면 TimescaleDB 확장을
  추가하는 것을 권장합니다.
