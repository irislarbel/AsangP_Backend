from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import validate_api_key
from app.services.congestion_service import CongestionService
from app.api.schemas.congestion import CongestionDataCreate, CongestionResponse

router = APIRouter()

@router.post("/", response_model=CongestionResponse, status_code=status.HTTP_200_OK)
def record_congestion(
    data_in: CongestionDataCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    ESP32용: 스캔한 WiFi/BT 기기 수를 서버에 전송합니다. (API Key 인증 필요)
    전송 후 해당 기기가 속한 장소(Space)의 wifi/bt 임계값들을 반환합니다.
    """
    service = CongestionService(db)
    thresholds = service.record_congestion(data_in)
    return CongestionResponse(**thresholds)
