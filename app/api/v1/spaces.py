from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.congestion_service import CongestionService
from app.services.space_service import SpaceService
from app.api.schemas.space import SpaceHistoryResponse, SpacePeaksResponse

router = APIRouter()

@router.get("/{space_id}/status")
def get_space_status(space_id: int, db: Session = Depends(get_db)):
    """
    프론트엔드용: 특정 공간의 현재 혼잡도 상태를 반환합니다.
    """
    service = CongestionService(db)
    # 해당 공간에 속한 장치들의 최신 데이터를 가져와서 반환
    return service.get_space_current_status(space_id)

@router.get("/{space_id}/history", response_model=SpaceHistoryResponse)
def get_space_history(
    space_id: int, 
    target_date: Optional[date] = None, 
    db: Session = Depends(get_db)
):
    """
    프론트엔드용: 특정 공간의 이력 데이터를 반환합니다. (10분 단위)
    target_date를 지정하지 않으면 '오늘'을 기준으로 조회합니다.
    """
    service = SpaceService(db)
    return service.get_history(space_id, target_date)

@router.get("/{space_id}/peaks", response_model=SpacePeaksResponse)
def get_space_peaks(
    space_id: int, 
    target_date: date, 
    threshold: int = 70,
    db: Session = Depends(get_db)
):
    """
    프론트엔드용: 과거 7일간의 혼잡도 피크 데이터 및 추세를 반환합니다.
    """
    service = SpaceService(db)
    return service.get_peaks(space_id, target_date, threshold)

