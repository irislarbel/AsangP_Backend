from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_capacity: int = Field(default=50, gt=0)

class SpaceCreate(SpaceBase):
    pass

class SpaceUpdate(SpaceBase):
    name: Optional[str] = None
    max_capacity: Optional[int] = Field(default=None, gt=0)

class Space(SpaceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class HistoryPoint(BaseModel):
    time: str  # "HH:MM" 형식
    congestion_level: int

class SpaceHistoryResponse(BaseModel):
    target: List[HistoryPoint] # 선택한 날짜 (또는 오늘)
    comparison: List[HistoryPoint] # 선택한 날짜의 일주일 전

class PeakDayData(BaseModel):
    date: str
    peak_ranges: List[str]
    max_congestion: Optional[int] = None
    daily_trend: List[Optional[int]]

class SpacePeaksResponse(BaseModel):
    space_id: int
    target_date: str
    threshold: int
    data: List[PeakDayData]
