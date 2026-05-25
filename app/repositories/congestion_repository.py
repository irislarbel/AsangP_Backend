from sqlalchemy.orm import Session
from app.models.models import CongestionData, RawScannerData

class CongestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, device_id: str, count: float, result: str):
        """계산된 count와 판정 결과(result)를 함께 저장합니다."""
        db_data = CongestionData(
            device_id=device_id,
            count=count,
            result=result
        )
        self.db.add(db_data)
        return db_data

    def create_raw_log(self, device_id: str, wifi_count: int, bt_count: int):
        """원본 측정 데이터를 로그로 남깁니다."""
        raw_log = RawScannerData(
            device_id=device_id,
            wifi_count=wifi_count,
            bt_count=bt_count
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
