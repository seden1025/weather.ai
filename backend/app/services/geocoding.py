"""OpenStreetMap Nominatim을 이용한 주소 → 좌표 변환 (무료, 키 불필요).

Nominatim 사용 정책상 User-Agent를 명시해야 하고, 초당 1회 이하로 호출해야
한다 (https://operations.osmfoundation.org/policies/nominatim/). 학생
동아리 프로젝트 트래픽 규모에서는 별도 쓰로틀링 없이도 문제되지 않는다.
"""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "weather-ai-club-project/1.0 (student project; contact via GitHub issues)"


async def search_address(query: str, limit: int = 5) -> list[dict]:
    params = {
        "q": query,
        "format": "json",
        "countrycodes": "kr",
        "limit": limit,
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    return [
        {
            "display_name": item["display_name"],
            "lat": float(item["lat"]),
            "lon": float(item["lon"]),
        }
        for item in data
    ]
