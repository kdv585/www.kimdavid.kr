import os
import httpx
from typing import List, Dict, Any, Optional


class PlaceService:
    """실제 장소 데이터 서비스 (카카오 로컬 API)"""

    def __init__(self):
        self.kakao_api_key = os.getenv("KAKAO_REST_API_KEY", "")
        self.kakao_base_url = "https://dapi.kakao.com/v2/local"

    async def search_places(
        self,
        query: str,
        category: str,
        location: str,
        radius: int = 5000
    ) -> List[Dict[str, Any]]:
        """카카오 로컬 API로 장소 검색"""
        if not self.kakao_api_key:
            return []

        try:
            # 지역명을 좌표로 변환 (간단한 예시 - 실제로는 주소 검색 API 사용)
            # 여기서는 키워드 검색 사용
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"KakaoAK {self.kakao_api_key}"
                }
                
                # 키워드 검색
                search_query = f"{location} {query}"
                response = await client.get(
                    f"{self.kakao_base_url}/search/keyword.json",
                    headers=headers,
                    params={
                        "query": search_query,
                        "category_group_code": self._get_category_code(category),
                        "radius": radius,
                        "size": 15,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

                places = []
                for item in data.get("documents", [])[:10]:
                    places.append({
                        "id": item.get("id"),
                        "name": item.get("place_name", ""),
                        "address": item.get("address_name", ""),
                        "road_address": item.get("road_address_name", ""),
                        "phone": item.get("phone", ""),
                        "category": item.get("category_name", ""),
                        "x": float(item.get("x", 0)),
                        "y": float(item.get("y", 0)),
                        "place_url": item.get("place_url", ""),
                        "rating": 4.0,  # 카카오 API에는 평점이 없으므로 기본값
                    })
                return places
        except Exception as e:
            print(f"장소 검색 실패 ({category}): {e}")
            return []

    def _get_category_code(self, category: str) -> Optional[str]:
        """카테고리를 카카오 카테고리 코드로 변환"""
        category_map = {
            "카페": "CE7",  # 카페
            "맛집": "FD6",  # 음식점
            "산책": "PK6",  # 공원
            "쇼핑": "MT1",  # 대형마트
            "문화": "CT1",  # 문화시설
            "야외활동": "PK6",  # 공원
            "실내활동": "CT1",  # 문화시설
        }
        return category_map.get(category)

    async def get_cafes(self, location: str) -> List[Dict[str, Any]]:
        """카페 검색"""
        return await self.search_places("카페", "카페", location)

    async def get_restaurants(self, location: str, cuisine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """맛집 검색"""
        query = "맛집"
        if cuisine_type:
            query = f"{cuisine_type} {query}"
        return await self.search_places(query, "맛집", location)

    async def get_parks(self, location: str) -> List[Dict[str, Any]]:
        """공원 검색 (산책)"""
        return await self.search_places("공원", "산책", location)

    async def get_shopping(self, location: str) -> List[Dict[str, Any]]:
        """쇼핑몰 검색"""
        return await self.search_places("쇼핑몰", "쇼핑", location)

    async def get_cultural_places(self, location: str, place_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """문화시설 검색"""
        query = "문화시설"
        if place_type:
            query = place_type
        return await self.search_places(query, "문화", location)

    async def get_indoor_activities(self, location: str, activity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """실내활동 장소 검색"""
        query_map = {
            "보드게임": "보드게임카페",
            "방탈출": "방탈출",
            "볼링": "볼링장",
            "당구": "당구장",
            "노래방": "노래방",
            "오락실": "오락실",
            "수공예": "수공예",
        }
        query = query_map.get(activity_type, "실내활동") if activity_type else "실내활동"
        return await self.search_places(query, "실내활동", location)

    async def get_outdoor_activities(self, location: str, activity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """야외활동 장소 검색"""
        query_map = {
            "등산": "등산로",
            "자전거": "자전거길",
            "피크닉": "피크닉",
            "캠핑": "캠핑장",
        }
        query = query_map.get(activity_type, "야외활동") if activity_type else "야외활동"
        return await self.search_places(query, "야외활동", location)

