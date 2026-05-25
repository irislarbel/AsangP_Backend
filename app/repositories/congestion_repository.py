from sqlalchemy.orm import Session
from app.models.models import CongestionData, RawScannerData, get_kst_now

class CongestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, device_id: str, count: float, result: str):
        """기존 데이터가 있으면 덮어쓰고, 없으면 새로 생성합니다."""
        db_data = self.db.query(CongestionData).filter(CongestionData.device_id == device_id).first()
        
        if db_data:
            db_data.count = count
            db_data.result = result
            db_data.timestamp = get_kst_now()
        else:
            db_data = CongestionData(
                device_id=device_id,
                count=count,
                result=result
            )
            self.db.add(db_data)
        
        return db_data

    def create_raw_log(self, device_id: str, wifi_count: int, bt_count: int, count: float, result: str):
        """원본 측정 데이터와 계산 결과를 함께 로그로 남깁니다."""
        raw_log = RawScannerData(
            device_id=device_id,
            wifi_count=wifi_count,
            bt_count=bt_count,
            count=count,
            result=result
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
