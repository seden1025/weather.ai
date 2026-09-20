# Weather AI

지도학습 기반 날씨 예측 AI + 이상치 원인 조사 웹 서비스.

## 사전 설치 필요

이 컴퓨터에는 아직 아래가 설치되어 있지 않습니다. 먼저 설치하세요.

- **Python 3.11+**: https://www.python.org/downloads/ (설치 시 "Add python.exe to PATH" 체크)
- **Node.js 20 LTS**: https://nodejs.org/
- **Docker Desktop** (로컬 DB용, 선택): https://www.docker.com/products/docker-desktop/

## 폴더 구조

```
weather-ai/
  backend/    FastAPI 서버 (API, DB 모델, 이상치 탐지, 뉴스 연동)
  frontend/   Next.js 웹 서비스
  docker-compose.yml   로컬 PostgreSQL(TimescaleDB) 실행용
```

## 실행 순서

1. DB 실행 (Docker 사용 시)
   ```bash
   docker compose up -d
   ```

2. 백엔드
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   # .env에 KMA_API_KEY, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 입력
   uvicorn app.main:app --reload
   ```

3. 프론트엔드 (새 터미널)
   ```bash
   cd frontend
   npm install
   copy .env.local.example .env.local
   npm run dev
   ```

4. http://localhost:3000 접속 (백엔드는 http://localhost:8000/docs)

## 다음 단계 (미구현)

- 기상자료개방포털 5년치 과거 데이터 배치 적재 스크립트
- 이상치 탐지 스케줄러(APScheduler)로 매일 자동 실행 + `anomaly_events` 테이블 저장
- XGBoost/PyTorch 기반 예측 모델 학습 파이프라인
- 지도(Leaflet) 기반 지역별 날씨/이상치 시각화
