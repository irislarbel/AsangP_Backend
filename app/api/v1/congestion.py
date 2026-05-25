from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import validate_api_key
from app.services.congestion_service import CongestionService
from app.api.schemas.congestion import CongestionDataCreate

router = APIRouter()

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
def record_congestion(
    data_in: CongestionDataCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(validate_api_key)
):
    """
    ESP32용: 스캔한 WiFi/BT 기기 수를 서버에 전송합니다. (API Key 인증 필요)
    전송 성공 시 응답 바디 없이 204 상태 코드만 반환합니다.
    """
    service = CongestionService(db)
    service.record_congestion(data_in)
    return
