from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.device_service import DeviceService
from app.api.schemas.device import ScannerDevice, ScannerDeviceCreate, ScannerDeviceUpdate

router = APIRouter()

@router.get("/", response_model=List[ScannerDevice])
def read_devices(db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.get_all_devices()

@router.get("/{device_id}", response_model=ScannerDevice)
def read_device(device_id: str, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.get_device(device_id)

@router.post("/", response_model=ScannerDevice)
def register_device(device_in: ScannerDeviceCreate, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.register_device(device_in)

@router.patch("/{device_id}", response_model=ScannerDevice)
def update_device(device_id: str, device_in: ScannerDeviceUpdate, db: Session = Depends(get_db)):
    service = DeviceService(db)
    return service.update_device(device_id, device_in)
