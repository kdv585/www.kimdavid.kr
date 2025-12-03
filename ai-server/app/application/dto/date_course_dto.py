from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DateCourseDTO(BaseModel):
    """데이트코스 DTO"""
    id: Optional[str] = None
    title: str
    description: str
    location: str
    category: str
    duration: int = Field(gt=0, description="소요 시간(분)")
    price_range: str = Field(description="가격대: 저렴, 보통, 비쌈")
    tags: List[str]
    rating: float = Field(ge=0, le=5, description="평점 (0~5)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PreferenceDTO(BaseModel):
    """선호도 DTO"""
    budget: str = Field(description="예산: 저렴, 보통, 비쌈")
    location: str
    interests: List[str] = Field(description="관심사 태그 리스트")
    date: str = Field(description="날짜: YYYY-MM-DD 형식")
    time_of_day: str = Field(description="시간대: 아침, 점심, 오후, 저녁, 밤")
    weather: Optional[str] = None


class RecommendDateCourseRequest(BaseModel):
    """데이트코스 추천 요청 DTO"""
    preference: PreferenceDTO


class RecommendDateCourseResponse(BaseModel):
    """데이트코스 추천 응답 DTO"""
    courses: List[DateCourseDTO]
    count: int

