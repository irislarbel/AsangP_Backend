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
        ESP32로부터 데이터를 받아 한 번만 계산하고, 
        현재 상태는 덮어쓰기(upsert), 이력은 원본 데이터와 함께 로그로 남깁니다.
        """
        device = self.device_repository.get_by_id(data_in.device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"{data_in.device_id}번 장치는 등록되지 않았어요~")
        
        # 1. 점수 계산 (WiFi + BT * 0.5) - 한 번만 수행
        calculated_count = data_in.wifi_count + (data_in.bt_count * 0.5)
        
        # 2. 혼잡도 판정 (max_capacity 대비 백분율)
        space = device.space
        if space and space.max_capacity and space.max_capacity > 0:
            congestion_level = max(0, min(100, round((calculated_count / space.max_capacity) * 100)))
        else:
            congestion_level = 0

        # 3. 원본 로그 기록 (계산 결과 포함)
        self.repository.create_raw_log(
            device_id=data_in.device_id,
            wifi_count=data_in.wifi_count,
            bt_count=data_in.bt_count,
            count=calculated_count,
            congestion_level=congestion_level
        )
        
        # 4. 장치 마지막 활동 시간 업데이트
        self.device_repository.update_last_seen(data_in.device_id)

        # 5. 현재 혼잡도 상태 업데이트 (덮어쓰기)
        self.repository.upsert(
            device_id=data_in.device_id, 
            count=calculated_count, 
            congestion_level=congestion_level
        )
        
        # 최종 commit
        self.db.commit()
        
        # Space에 설정된 임계값 반환 (Space가 없으면 기본값 반환)
        wifi_threshold = space.wifi_rssi_threshold if space else -75
        bt_threshold = space.bt_rssi_threshold if space else -70
        
        return {
            "wifi_rssi_threshold": wifi_threshold,
            "bt_rssi_threshold": bt_threshold
        }

    def get_space_current_status(self, space_id: int):
        """특정 공간의 현재 혼잡도 상태와 판정 결과를 반환합니다."""
        # 1. 공간 존재 여부 확인
        from app.repositories.space_repository import SpaceRepository
        space_repo = SpaceRepository(self.db)
        space = space_repo.get_by_id(space_id)
        if not space:
            raise HTTPException(status_code=404, detail=f"{space_id}번 장소도 없어요~")

        # 2. 해당 공간의 장치 확인
        devices = self.db.query(ScannerDevice).filter(ScannerDevice.space_id == space_id).all()
        if not devices:
            # 공간은 있지만 연결된 장치가 없는 경우
            return {
                "space_id": space_id,
                "space_name": space.name,
                "congestion_level": 0,
                "last_update": None
            }

        # 해당 공간의 모든 장치로부터 최신 데이터를 수집하여 가장 최근의 것을 선택합니다.
        congestion_level = 0
        last_update = None
        
        for device in devices:
            latest = self.repository.get_latest_by_device(device.id)
            if latest and (last_update is None or latest.timestamp > last_update):
                congestion_level = latest.congestion_level
                last_update = latest.timestamp

        return {
            "space_id": space_id,
            "space_name": space.name,
            "congestion_level": congestion_level,
            "last_update": last_update
        }
