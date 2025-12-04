"""
의존성 주입 설정
"""
from functools import lru_cache
from app.domain.repositories.date_course_repository import DateCourseRepository
from app.domain.services.ai_service import AIService
from app.infrastructure.repositories.in_memory_date_course_repository import InMemoryDateCourseRepository
from app.infrastructure.services.openai_service import OpenAIService
from app.infrastructure.services.culture_service import CultureService
from app.infrastructure.services.place_service import PlaceService
from app.application.use_cases.recommend_date_course import RecommendDateCourseUseCase


@lru_cache()
def get_date_course_repository() -> DateCourseRepository:
    """데이트코스 저장소 의존성"""
    return InMemoryDateCourseRepository()


@lru_cache()
def get_culture_service() -> CultureService:
    """문화 데이터 서비스 의존성"""
    return CultureService()


@lru_cache()
def get_place_service() -> PlaceService:
    """장소 데이터 서비스 의존성"""
    return PlaceService()


@lru_cache()
def get_ai_service() -> AIService:
    """AI 서비스 의존성"""
    return OpenAIService(
        culture_service=get_culture_service(),
        place_service=get_place_service()
    )


@lru_cache()
def get_recommend_date_course_use_case() -> RecommendDateCourseUseCase:
    """데이트코스 추천 유스케이스 의존성"""
    repository = get_date_course_repository()
    ai_service = get_ai_service()
    return RecommendDateCourseUseCase(repository, ai_service)

