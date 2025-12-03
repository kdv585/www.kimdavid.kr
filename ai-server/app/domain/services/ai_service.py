from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference


class AIService(ABC):
    """AI 서비스 인터페이스"""

    @abstractmethod
    async def recommend_date_courses(
        self, 
        preference: Preference,
        existing_courses: List[DateCourse]
    ) -> List[DateCourse]:
        """선호도 기반 데이트코스 추천"""
        pass

