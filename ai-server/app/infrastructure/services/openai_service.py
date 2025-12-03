import os
import json
from typing import List
from datetime import datetime
from app.domain.entities.date_course import DateCourse
from app.domain.value_objects.preference import Preference
from app.domain.services.ai_service import AIService


class OpenAIService(AIService):
    """OpenAI 기반 AI 서비스 구현"""

    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.model = model or os.getenv("AI_MODEL", "gpt-4")
        self.base_url = "https://api.openai.com/v1"

    async def recommend_date_courses(
        self,
        preference: Preference,
        existing_courses: List[DateCourse]
    ) -> List[DateCourse]:
        """
        AI를 통한 데이트코스 추천
        
        실제 구현에서는 OpenAI API를 호출하지만,
        현재는 기존 코스들을 기반으로 추천 로직을 구현
        """
        # 기존 코스가 있으면 우선 반환
        if existing_courses:
            return existing_courses[:3]  # 상위 3개 반환

        # AI 추천이 필요한 경우 (향후 OpenAI API 연동)
        # 현재는 기본 추천 코스 생성
        # 시간대에 따라 기본 duration 설정
        time_duration_map = {
            "아침": 120,
            "점심": 180,
            "오후": 240,
            "저녁": 180,
            "밤": 150
        }
        default_duration = time_duration_map.get(preference.time_of_day, 180)
        
        recommended = DateCourse(
            id=None,
            title=f"{preference.location} 데이트 코스",
            description=f"예산: {preference.budget}, 날짜: {preference.date}, 시간대: {preference.time_of_day}, 날씨: {preference.weather or '맑음'}, 관심사: {', '.join(preference.interests)}",
            location=preference.location,
            category=preference.interests[0] if preference.interests else "일반",
            duration=default_duration,
            price_range=preference.budget,
            tags=preference.interests,
            rating=4.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        return [recommended]

    def _build_prompt(self, preference: Preference) -> str:
        """AI 프롬프트 생성"""
        return f"""
        다음 조건에 맞는 데이트코스를 추천해주세요:
        - 예산: {preference.budget}
        - 날짜: {preference.date}
        - 시간대: {preference.time_of_day}
        - 위치: {preference.location}
        - 관심사: {', '.join(preference.interests)}
        - 날씨: {preference.weather or '맑음'}
        
        JSON 형식으로 응답해주세요.
        """

