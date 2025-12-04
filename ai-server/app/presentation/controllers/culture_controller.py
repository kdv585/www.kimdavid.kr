from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.infrastructure.services.culture_service import CultureService


class CultureController:
    """문화 데이터 컨트롤러"""

    def __init__(self):
        self.culture_service = CultureService()
        self.router = APIRouter(prefix="/api/v1/culture", tags=["culture"])

        # 라우트 등록
        self.router.add_api_route(
            "/movies",
            self.get_movies,
            methods=["GET"],
            response_model=dict
        )
        self.router.add_api_route(
            "/exhibitions",
            self.get_exhibitions,
            methods=["GET"],
            response_model=dict
        )
        self.router.add_api_route(
            "/performances",
            self.get_performances,
            methods=["GET"],
            response_model=dict
        )

    async def get_movies(
        self,
        location: str = Query(..., description="지역"),
        date: str = Query(..., description="날짜 (YYYY-MM-DD)")
    ) -> dict:
        """현재 상영 중인 영화 가져오기"""
        try:
            movies = await self.culture_service.get_movies(location, date)
            return {"movies": movies}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"영화 데이터 가져오기 실패: {str(e)}")

    async def get_exhibitions(
        self,
        location: str = Query(..., description="지역"),
        date: str = Query(..., description="날짜 (YYYY-MM-DD)")
    ) -> dict:
        """전시회 정보 가져오기"""
        try:
            exhibitions = await self.culture_service.get_exhibitions(location, date)
            return {"exhibitions": exhibitions}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"전시회 데이터 가져오기 실패: {str(e)}")

    async def get_performances(
        self,
        location: str = Query(..., description="지역"),
        date: str = Query(..., description="날짜 (YYYY-MM-DD)"),
        genre: Optional[str] = Query(None, description="장르 (뮤지컬, 연극, 콘서트 등)")
    ) -> dict:
        """공연 정보 가져오기"""
        try:
            performances = await self.culture_service.get_performances(location, date, genre)
            return {"performances": performances}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"공연 데이터 가져오기 실패: {str(e)}")

