from typing import List
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference
from app.domain.repositories.date_course_repository import DateCourseRepository
from app.domain.services.ai_service import AIService


class RecommendDateCourseUseCase:
    """데이트코스 추천 유스케이스"""

    def __init__(
        self,
        date_course_repository: DateCourseRepository,
        ai_service: AIService
    ):
        self._date_course_repository = date_course_repository
        self._ai_service = ai_service

    async def execute(self, preference: Preference) -> List[DateCourse]:
        """
        선호도 기반 데이트코스 추천 실행
        
        Args:
            preference: 사용자 선호도
            
        Returns:
            추천된 데이트코스 리스트
        """
        # 기존 데이트코스 조회
        existing_courses = await self._date_course_repository.find_by_preference(preference)
        
        # AI 서비스를 통한 추천
        recommended_courses = await self._ai_service.recommend_date_courses(
            preference=preference,
            existing_courses=existing_courses
        )
        
        return recommended_courses

