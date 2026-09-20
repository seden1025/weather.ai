from fastapi import APIRouter

from app.services.stations import STATIONS, find_nearest

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("")
def list_stations():
    return STATIONS


@router.get("/nearest")
def nearest_station(lat: float, lon: float):
    return find_nearest(lat, lon)
