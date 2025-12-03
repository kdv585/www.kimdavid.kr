from fastapi import APIRouter
from app.presentation.controllers.date_course_controller import DateCourseController
from app.application.use_cases.recommend_date_course import RecommendDateCourseUseCase


def create_date_course_routes(
    recommend_use_case: RecommendDateCourseUseCase
) -> APIRouter:
    """데이트코스 라우트 생성"""
    controller = DateCourseController(recommend_use_case)
    return controller.router

