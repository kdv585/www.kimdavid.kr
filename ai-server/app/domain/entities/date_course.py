from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class DateCourse:
    """데이트코스 도메인 엔티티"""
    id: Optional[str]
    title: str
    description: str
    location: str
    category: str
    duration: int  # 분 단위
    price_range: str  # "저렴", "보통", "비쌈"
    tags: List[str]
    rating: float
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        if self.rating < 0 or self.rating > 5:
            raise ValueError("평점은 0~5 사이여야 합니다.")
        if self.duration <= 0:
            raise ValueError("소요 시간은 0보다 커야 합니다.")

