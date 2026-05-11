from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.device_repository import DeviceRepository
from app.repositories.space_repository import SpaceRepository
from app.api.schemas.device import ScannerDeviceCreate, ScannerDeviceUpdate

class DeviceService:
    def __init__(self, db: Session):
        self.repository = DeviceRepository(db)
        self.space_repository = SpaceRepository(db)

    def get_all_devices(self):
        return self.repository.get_all()

    def get_device(self, device_id: str):
        device = self.repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found"
            )
        return device

    def register_device(self, device_in: ScannerDeviceCreate):
        # space_id 유효성 검사
        if not self.space_repository.get_by_id(device_in.space_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Space with id {device_in.space_id} does not exist"
            )
        
        # 이미 존재하는 기기인지 확인
        if self.repository.get_by_id(device_in.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device with id {device_in.id} already registered"
            )
            
        return self.repository.create(device_in)

    def update_device(self, device_id: str, device_in: ScannerDeviceUpdate):
        device = self.repository.update(device_id, device_in)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with id {device_id} not found"
            )
        return device
