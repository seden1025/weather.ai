"""카카오 로컬 API를 이용한 주소 → 좌표 변환.

https://developers.kakao.com/docs/latest/ko/local/dev-guide#address-coord
REST API 키 발급 필요 (카카오 개발자센터 → 내 애플리케이션 → 앱 키).
"""

import httpx

from app.core.config import settings

KAKAO_ADDRESS_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_KEYWORD_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"


async def search_address(query: str, limit: int = 5) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {settings.kakao_rest_api_key}"}
    params = {"query": query, "size": limit}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(KAKAO_ADDRESS_SEARCH_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        documents = data.get("documents", [])

        # 지번/도로명 주소로 못 찾으면(동네 이름, 건물명 등) 키워드 검색으로 재시도
        if not documents:
            resp = await client.get(KAKAO_KEYWORD_SEARCH_URL, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            documents = data.get("documents", [])
            return [
                {
                    "display_name": item["address_name"] or item["place_name"],
                    "lat": float(item["y"]),
                    "lon": float(item["x"]),
                }
                for item in documents
            ]

    return [
        {
            "display_name": item["address_name"],
            "lat": float(item["y"]),
            "lon": float(item["x"]),
        }
        for item in documents
    ]
