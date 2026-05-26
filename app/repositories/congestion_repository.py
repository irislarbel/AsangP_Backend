from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from app.models.models import CongestionData, RawScannerData, ScannerDevice, get_kst_now

class CongestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, device_id: str, count: float, congestion_level: int):
        """기존 데이터가 있으면 덮어쓰고, 없으면 새로 생성합니다. (원자적 Upsert)"""
        stmt = insert(CongestionData).values(
            device_id=device_id,
            count=count,
            congestion_level=congestion_level,
            timestamp=get_kst_now()
        )
        
        # device_id 충돌 시 count, congestion_level, timestamp 업데이트
        stmt = stmt.on_conflict_do_update(
            index_elements=['device_id'],
            set_={
                'count': count,
                'congestion_level': congestion_level,
                'timestamp': get_kst_now()
            }
        )
        
        self.db.execute(stmt)
        # flush를 호출하여 영속성 컨텍스트에 반영 (필요 시)
        self.db.flush()
        
        # 반환값은 쿼리 결과로 가져옴 (성능 최적화가 필요하다면 이 부분 조정 가능)
        return self.db.query(CongestionData).filter(CongestionData.device_id == device_id).first()

    def create_raw_log(self, device_id: str, wifi_count: int, bt_count: int, count: float, congestion_level: int):
        """원본 측정 데이터와 계산 결과를 함께 로그로 남깁니다."""
        raw_log = RawScannerData(
            device_id=device_id,
            wifi_count=wifi_count,
            bt_count=bt_count,
            count=count,
            congestion_level=congestion_level
        )
        self.db.add(raw_log)
        return raw_log

    def get_latest_by_device(self, device_id: str):
        return self.db.query(CongestionData)\
            .filter(CongestionData.device_id == device_id)\
            .order_by(CongestionData.timestamp.desc())\
            .first()

    def get_history_by_device(self, device_id: str, limit: int = 100):
        return self.db.query(CongestionData)\
            .filter(CongestionData.device_id == device_id)\
            .order_by(CongestionData.timestamp.desc())\
            .limit(limit)\
            .all()

    def get_raw_history_by_space(self, space_id: int, start_time: datetime, end_time: datetime):
        """특정 공간의 모든 디바이스에서 발생한 로그를 특정 기간 동안 가져옵니다."""
        return self.db.query(RawScannerData)\
            .join(ScannerDevice)\
            .filter(ScannerDevice.space_id == space_id)\
            .filter(RawScannerData.timestamp >= start_time)\
            .filter(RawScannerData.timestamp <= end_time)\
            .order_by(RawScannerData.timestamp.asc())\
            .all()
