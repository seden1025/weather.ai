from datetime import date, datetime

from pydantic import BaseModel


class PredictionIn(BaseModel):
    sky_condition: str
    wind_feel: str
    predicted_max_temp: float
    predicted_sky_condition: str | None = None
    memo: str | None = None


class PredictionOut(BaseModel):
    id: int
    station_id: str
    predict_date: date
    sky_condition: str
    wind_feel: str
    memo: str | None = None
    predicted_max_temp: float
    predicted_sky_condition: str | None = None
    ai_predicted_max_temp: float | None = None
    ai_predicted_sky_condition: str | None = None
    actual_max_temp: float | None = None
    actual_rained: bool | None = None
    created_at: datetime

    class Config:
        from_attributes = True
