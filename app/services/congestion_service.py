from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.congestion_repository import CongestionRepository
from app.repositories.device_repository import DeviceRepository
from app.api.schemas.congestion import CongestionDataCreate
from app.models.models import ScannerDevice

class CongestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = CongestionRepository(db)
        self.device_repository = DeviceRepository(db)

    def record_congestion(self, data_in: CongestionDataCreate):
        """
        ESP32로부터 데이터를 받아 가공하고, 판정 결과를 저장하며 원본 로그를 남깁니다.
        """
        device = self.device_repository.get_by_id(data_in.device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {data_in.device_id} not registered")
        
        # 1. 원본 로그 기록
        self.repository.create_raw_log(
            device_id=data_in.device_id,
            wifi_count=data_in.wifi_count,
            bt_count=data_in.bt_count
        )

        # 2. 점수 계산 (WiFi + BT * 0.5)
        calculated_count = data_in.wifi_count + (data_in.bt_count * 0.5)
        
        # 3. 혼잡도 판정
        space = device.space
        if calculated_count <= space.low_threshold:
            result = "여유"
        elif calculated_count <= space.medium_threshold:
            result = "보통"
        else:
            result = "혼잡"
        
        self.device_repository.update_last_seen(data_in.device_id)
        result_data = self.repository.create(
            device_id=data_in.device_id, 
            count=calculated_count, 
            result=result
        )
        
        # 원자성 보장을 위해 서비스 레이어에서 최종 commit
        self.db.commit()
        self.db.refresh(result_data)
        
        return result_data

    def get_space_current_status(self, space_id: int):
        """특정 공간의 현재 혼잡도 상태와 판정 결과를 반환합니다."""
        devices = self.db.query(ScannerDevice).filter(ScannerDevice.space_id == space_id).all()
        if not devices:
            raise HTTPException(status_code=404, detail="No devices in this space")

        # 첫 번째 장치의 최신 데이터를 가져옵니다.
        device = devices[0]
        latest = self.repository.get_latest_by_device(device.id)
        
        count = 0.0
        result = "데이터 없음"
        last_update = None
        
        if latest:
            count = latest.count
            result = latest.result
            last_update = latest.timestamp

        return {
            "space_id": space_id,
            "space_name": device.space.name,
            "count": count,
            "result": result,
            "last_update": last_update
        }
