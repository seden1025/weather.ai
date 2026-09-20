from datetime import datetime

from pydantic import BaseModel


class ObservationOut(BaseModel):
    station_id: str
    observed_at: datetime
    temperature: float | None = None
    precipitation: float | None = None
    wind_speed: float | None = None
    humidity: float | None = None
    pressure: float | None = None

    class Config:
        from_attributes = True


class ForecastOut(BaseModel):
    station_id: str
    target_time: datetime
    kma_forecast_temp: float | None = None
    ai_forecast_temp: float | None = None
