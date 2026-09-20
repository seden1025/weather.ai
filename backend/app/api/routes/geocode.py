from fastapi import APIRouter

from app.services.geocoding import search_address

router = APIRouter(prefix="/geocode", tags=["geocode"])


@router.get("/search")
async def geocode_search(q: str):
    return await search_address(q)
