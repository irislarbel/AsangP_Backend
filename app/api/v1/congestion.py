from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.congestion_service import CongestionService
from app.api.schemas.congestion import CongestionData, CongestionDataCreate

router = APIRouter()

@router.post("/", response_model=CongestionData)
def record_congestion(data_in: CongestionDataCreate, db: Session = Depends(get_db)):
    """
    ESP32용: 스캔한 WiFi/BT 기기 수를 서버에 전송합니다.
    """
    service = CongestionService(db)
    return service.record_congestion(data_in)
