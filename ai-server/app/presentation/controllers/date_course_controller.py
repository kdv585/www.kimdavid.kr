from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.application.use_cases.recommend_date_course import RecommendDateCourseUseCase
from app.application.dto.date_course_dto import (
    RecommendDateCourseRequest,
    RecommendDateCourseResponse,
    DateCourseDTO,
    PreferenceDTO
)
from app.domain.value_objects.preference import Preference
from app.domain.entities.date_course import DateCourse


def date_course_entity_to_dto(entity: DateCourse) -> DateCourseDTO:
    """엔티티를 DTO로 변환"""
    return DateCourseDTO(
        id=entity.id,
        title=entity.title,
        description=entity.description,
        location=entity.location,
        category=entity.category,
        duration=entity.duration,
        price_range=entity.price_range,
        tags=entity.tags,
        rating=entity.rating,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )


def preference_dto_to_value_object(dto: PreferenceDTO) -> Preference:
    """DTO를 값 객체로 변환"""
    # interestDetails를 딕셔너리로 변환
    interest_details = None
    if dto.interestDetails:
        interest_details = {
            detail.interest: detail.details
            for detail in dto.interestDetails
        }
    
    return Preference(
        budget=dto.budget,
        location=dto.location,
        interests=dto.interests,
        date=dto.date,
        time_of_day=dto.time_of_day,
        interest_details=interest_details,
        weather=dto.weather
    )


class DateCourseController:
    """데이트코스 컨트롤러"""

    def __init__(self, recommend_use_case: RecommendDateCourseUseCase):
        self._recommend_use_case = recommend_use_case
        self.router = APIRouter(prefix="/api/v1/date-courses", tags=["date-courses"])

        # 라우트 등록
        self.router.add_api_route(
            "/recommend",
            self.recommend,
            methods=["POST"],
            response_model=RecommendDateCourseResponse
        )

    async def recommend(
        self,
        request: RecommendDateCourseRequest
    ) -> RecommendDateCourseResponse:
        """
        데이트코스 추천 API
        
        Args:
            request: 추천 요청 데이터
            
        Returns:
            추천된 데이트코스 리스트
        """
        try:
            # DTO를 도메인 객체로 변환
            preference = preference_dto_to_value_object(request.preference)

            # 유스케이스 실행
            courses = await self._recommend_use_case.execute(preference)

            # 엔티티를 DTO로 변환
            course_dtos = [date_course_entity_to_dto(course) for course in courses]

            return RecommendDateCourseResponse(
                courses=course_dtos,
                count=len(course_dtos)
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

