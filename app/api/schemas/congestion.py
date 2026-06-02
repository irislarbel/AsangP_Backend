from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CongestionDataCreate(BaseModel):
    device_id: str
    wifi_count: int
    bt_count: int

class CongestionData(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    device_id: str
    congestion_level: int
    timestamp: datetime

class CongestionResponse(BaseModel):
    wifi_rssi_threshold: int
    bt_rssi_threshold: int
