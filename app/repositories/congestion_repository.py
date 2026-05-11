from sqlalchemy.orm import Session
from app.models.models import CongestionData
from app.api.schemas.congestion import CongestionDataCreate

class CongestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data_in: CongestionDataCreate):
        db_data = CongestionData(
            device_id=data_in.device_id,
            wifi_count=data_in.wifi_count,
            bt_count=data_in.bt_count
        )
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return db_data

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
