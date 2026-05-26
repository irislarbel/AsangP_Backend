from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class SpaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    max_capacity: int = 50

class SpaceCreate(SpaceBase):
    pass

class SpaceUpdate(SpaceBase):
    name: Optional[str] = None
    max_capacity: Optional[int] = None

class Space(SpaceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class HistoryPoint(BaseModel):
    time: str  # "HH:MM" 형식
    congestion_level: int

class SpaceHistoryResponse(BaseModel):
    target: List[HistoryPoint] # 선택한 날짜 (또는 오늘)
    comparison: List[HistoryPoint] # 선택한 날짜의 일주일 전
