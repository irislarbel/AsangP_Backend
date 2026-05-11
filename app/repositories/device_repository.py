from sqlalchemy.orm import Session
from app.models.models import ScannerDevice
from app.api.schemas.device import ScannerDeviceCreate, ScannerDeviceUpdate
from datetime import datetime

class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(ScannerDevice).all()

    def get_by_id(self, device_id: str):
        return self.db.query(ScannerDevice).filter(ScannerDevice.id == device_id).first()

    def create(self, device_in: ScannerDeviceCreate):
        db_device = ScannerDevice(
            id=device_in.id,
            space_id=device_in.space_id,
            location_description=device_in.location_description
        )
        self.db.add(db_device)
        self.db.commit()
        self.db.refresh(db_device)
        return db_device

    def update(self, device_id: str, device_in: ScannerDeviceUpdate):
        db_device = self.get_by_id(device_id)
        if db_device:
            update_data = device_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_device, key, value)
            self.db.commit()
            self.db.refresh(db_device)
        return db_device

    def update_last_seen(self, device_id: str):
        db_device = self.get_by_id(device_id)
        if db_device:
            db_device.last_seen = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_device)
        return db_device
