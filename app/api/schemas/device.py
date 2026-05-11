from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ScannerDeviceBase(BaseModel):
    id: str
    space_id: int
    location_description: Optional[str] = None

class ScannerDeviceCreate(ScannerDeviceBase):
    pass

class ScannerDeviceUpdate(BaseModel):
    space_id: Optional[int] = None
    location_description: Optional[str] = None

class ScannerDevice(ScannerDeviceBase):
    model_config = ConfigDict(from_attributes=True)
    last_seen: datetime
