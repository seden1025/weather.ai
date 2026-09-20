"""주요 종관기상관측(ASOS) 지점 목록 (지점번호, 지점명, 위도, 경도).

기상자료개방포털의 96개 ASOS 지점 중 시/군 단위 대표 지점 위주로 추린
목록이다. 좌표는 지점 위치 기준 근사치이며, "가장 가까운 지점 찾기" 용도로
충분한 정밀도를 갖는다.
"""

import math

STATIONS = [
    {"id": "90", "name": "속초", "lat": 38.25, "lon": 128.56},
    {"id": "101", "name": "춘천", "lat": 37.90, "lon": 127.74},
    {"id": "105", "name": "강릉", "lat": 37.75, "lon": 128.89},
    {"id": "108", "name": "서울", "lat": 37.57, "lon": 126.98},
    {"id": "112", "name": "인천", "lat": 37.48, "lon": 126.62},
    {"id": "119", "name": "수원", "lat": 37.29, "lon": 127.01},
    {"id": "129", "name": "서산", "lat": 36.78, "lon": 126.49},
    {"id": "131", "name": "청주", "lat": 36.64, "lon": 127.44},
    {"id": "133", "name": "대전", "lat": 36.37, "lon": 127.37},
    {"id": "136", "name": "안동", "lat": 36.57, "lon": 128.71},
    {"id": "137", "name": "상주", "lat": 36.41, "lon": 128.16},
    {"id": "138", "name": "포항", "lat": 36.03, "lon": 129.38},
    {"id": "143", "name": "대구", "lat": 35.87, "lon": 128.60},
    {"id": "146", "name": "전주", "lat": 35.82, "lon": 127.15},
    {"id": "152", "name": "울산", "lat": 35.58, "lon": 129.33},
    {"id": "155", "name": "창원", "lat": 35.17, "lon": 128.57},
    {"id": "156", "name": "광주", "lat": 35.17, "lon": 126.89},
    {"id": "159", "name": "부산", "lat": 35.10, "lon": 129.03},
    {"id": "165", "name": "목포", "lat": 34.82, "lon": 126.38},
    {"id": "168", "name": "여수", "lat": 34.74, "lon": 127.74},
    {"id": "170", "name": "완도", "lat": 34.40, "lon": 126.70},
    {"id": "184", "name": "제주", "lat": 33.51, "lon": 126.53},
    {"id": "189", "name": "서귀포", "lat": 33.25, "lon": 126.56},
    {"id": "192", "name": "진주", "lat": 35.16, "lon": 128.04},
    {"id": "235", "name": "보령", "lat": 36.33, "lon": 126.56},
    {"id": "239", "name": "세종", "lat": 36.48, "lon": 127.29},
    {"id": "251", "name": "고창", "lat": 35.43, "lon": 126.70},
    {"id": "253", "name": "김해", "lat": 35.23, "lon": 128.89},
    {"id": "261", "name": "남해", "lat": 34.82, "lon": 127.93},
    {"id": "279", "name": "구미", "lat": 36.13, "lon": 128.32},
    {"id": "288", "name": "밀양", "lat": 35.49, "lon": 128.75},
]


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def find_nearest(lat: float, lon: float) -> dict:
    return min(STATIONS, key=lambda s: _haversine_km(lat, lon, s["lat"], s["lon"]))
