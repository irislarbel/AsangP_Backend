from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.congestion_service import CongestionService

router = APIRouter()

@router.get("/{space_id}/status")
def get_space_status(space_id: int, db: Session = Depends(get_db)):
    """
    프론트엔드용: 특정 공간의 현재 혼잡도 상태를 반환합니다.
    """
    service = CongestionService(db)
    # 해당 공간에 속한 장치들의 최신 데이터를 가져와서 반환
    return service.get_space_current_status(space_id)
