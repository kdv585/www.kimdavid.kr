from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference


class DateCourseRepository(ABC):
    """데이트코스 저장소 인터페이스"""

    @abstractmethod
    async def find_by_id(self, course_id: str) -> Optional[DateCourse]:
        """ID로 데이트코스 조회"""
        pass

    @abstractmethod
    async def find_by_preference(self, preference: Preference) -> List[DateCourse]:
        """선호도에 맞는 데이트코스 조회"""
        pass

    @abstractmethod
    async def find_all(self) -> List[DateCourse]:
        """모든 데이트코스 조회"""
        pass

    @abstractmethod
    async def save(self, course: DateCourse) -> DateCourse:
        """데이트코스 저장"""
        pass

