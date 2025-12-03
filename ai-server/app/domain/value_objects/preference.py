from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Preference:
    """사용자 선호도 값 객체"""
    budget: str  # "저렴", "보통", "비쌈"
    location: str
    interests: List[str]  # 관심사 태그
    date: str  # YYYY-MM-DD 형식
    time_of_day: str  # "아침", "점심", "오후", "저녁", "밤"
    weather: Optional[str] = None  # "맑음", "비", "눈" 등 (날짜 선택 시 자동 설정)

    def __post_init__(self):
        if self.budget not in ["저렴", "보통", "비쌈"]:
            raise ValueError("예산은 '저렴', '보통', '비쌈' 중 하나여야 합니다.")
        if not self.time_of_day:
            raise ValueError("시간대는 필수입니다.")

