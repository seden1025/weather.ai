from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import anomaly, geocode, stations, weather
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="Weather AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(anomaly.router)
app.include_router(stations.router)
app.include_router(geocode.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
