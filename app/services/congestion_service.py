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
        """ESP32로부터 데이터를 받아 저장하고 기기 상태를 갱신합니다."""
        device = self.device_repository.get_by_id(data_in.device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {data_in.device_id} not registered")
        
        self.device_repository.update_last_seen(data_in.device_id)
        return self.repository.create(data_in)

    def get_space_current_status(self, space_id: int):
        """특정 공간의 현재 혼잡도 상태를 반환합니다."""
        devices = self.db.query(ScannerDevice).filter(ScannerDevice.space_id == space_id).all()
        if not devices:
            raise HTTPException(status_code=404, detail="No devices in this space")

        total_wifi = 0
        total_bt = 0

        # 장치는 각 공간별로 하나라고 하셨으므로, 첫 번째 장치의 최신 데이터를 가져옵니다.
        device = devices[0]
        latest = self.repository.get_latest_by_device(device.id)
        
        if latest:
            total_wifi = latest.wifi_count
            total_bt = latest.bt_count
            last_update = latest.timestamp
        else:
            last_update = None

        return {
            "space_id": space_id,
            "space_name": device.space.name, # 공간 이름 포함
            "wifi_count": total_wifi,
            "bt_count": total_bt,
            "last_update": last_update
        }
