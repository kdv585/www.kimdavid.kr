from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Location:
    """위치 값 객체"""
    city: str
    district: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __post_init__(self):
        if not self.city or not self.district:
            raise ValueError("도시와 구/군은 필수입니다.")
        if self.latitude and (self.latitude < -90 or self.latitude > 90):
            raise ValueError("위도는 -90~90 사이여야 합니다.")
        if self.longitude and (self.longitude < -180 or self.longitude > 180):
            raise ValueError("경도는 -180~180 사이여야 합니다.")

    def __str__(self) -> str:
        return f"{self.city} {self.district}"

