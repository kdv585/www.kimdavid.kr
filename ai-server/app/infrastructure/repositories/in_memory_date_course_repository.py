from typing import List, Optional, Dict
from datetime import datetime
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference
from app.domain.repositories.date_course_repository import DateCourseRepository


class InMemoryDateCourseRepository(DateCourseRepository):
    """인메모리 데이트코스 저장소 구현"""

    def __init__(self):
        self._courses: Dict[str, DateCourse] = {}
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """샘플 데이터 초기화"""
        sample_courses = [
            DateCourse(
                id="1",
                title="한강 공원 산책",
                description="한강에서 즐기는 낭만적인 산책 코스",
                location="서울시 영등포구",
                category="야외활동",
                duration=120,
                price_range="저렴",
                tags=["산책", "자연", "무료"],
                rating=4.5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            DateCourse(
                id="2",
                title="카페 투어",
                description="트렌디한 카페들을 돌아보는 코스",
                location="서울시 강남구",
                category="카페",
                duration=180,
                price_range="보통",
                tags=["카페", "디저트", "인스타그램"],
                rating=4.3,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            DateCourse(
                id="3",
                title="미술관 관람",
                description="현대 미술 작품을 감상하는 문화 코스",
                location="서울시 종로구",
                category="문화",
                duration=150,
                price_range="보통",
                tags=["미술", "문화", "교육"],
                rating=4.7,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]
        for course in sample_courses:
            self._courses[course.id] = course

    async def find_by_id(self, course_id: str) -> Optional[DateCourse]:
        return self._courses.get(course_id)

    async def find_by_preference(self, preference: Preference) -> List[DateCourse]:
        """선호도에 맞는 데이트코스 필터링"""
        filtered = []
        for course in self._courses.values():
            # 예산 필터
            if course.price_range != preference.budget:
                continue
            # 위치 필터 (간단한 문자열 포함 체크)
            if preference.location not in course.location:
                continue
            # 관심사 태그 매칭
            if not any(tag in course.tags for tag in preference.interests):
                continue
            filtered.append(course)
        return filtered

    async def find_all(self) -> List[DateCourse]:
        return list(self._courses.values())

    async def save(self, course: DateCourse) -> DateCourse:
        if not course.id:
            course.id = str(len(self._courses) + 1)
        course.updated_at = datetime.now()
        self._courses[course.id] = course
        return course

