"""
의존성 주입 설정
"""
from app.domain.repositories.date_course_repository import DateCourseRepository
from app.domain.services.ai_service import AIService
from app.infrastructure.repositories.in_memory_date_course_repository import InMemoryDateCourseRepository
from app.infrastructure.services.openai_service import OpenAIService
from app.application.use_cases.recommend_date_course import RecommendDateCourseUseCase


def get_date_course_repository() -> DateCourseRepository:
    """데이트코스 저장소 의존성"""
    return InMemoryDateCourseRepository()


def get_ai_service() -> AIService:
    """AI 서비스 의존성"""
    return OpenAIService()


def get_recommend_date_course_use_case() -> RecommendDateCourseUseCase:
    """데이트코스 추천 유스케이스 의존성"""
    repository = get_date_course_repository()
    ai_service = get_ai_service()
    return RecommendDateCourseUseCase(repository, ai_service)

