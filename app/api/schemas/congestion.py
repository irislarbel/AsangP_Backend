from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CongestionDataBase(BaseModel):
    device_id: str
    wifi_count: int
    bt_count: int

class CongestionDataCreate(CongestionDataBase):
    pass

class CongestionData(CongestionDataBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    timestamp: datetime
