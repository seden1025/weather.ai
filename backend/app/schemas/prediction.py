from datetime import date, datetime

from pydantic import BaseModel


class PredictionIn(BaseModel):
    sky_condition: str
    wind_feel: str
    predicted_max_temp: float
    memo: str | None = None


class PredictionOut(BaseModel):
    id: int
    station_id: str
    predict_date: date
    sky_condition: str
    wind_feel: str
    memo: str | None = None
    predicted_max_temp: float
    ai_predicted_max_temp: float | None = None
    actual_max_temp: float | None = None
    created_at: datetime

    class Config:
        from_attributes = True
