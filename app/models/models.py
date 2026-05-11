from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Relationship: 1 Space can have many Devices
    devices = relationship("ScannerDevice", back_populates="space")

class ScannerDevice(Base):
    __tablename__ = "scanner_devices"

    id = Column(String, primary_key=True, index=True) # Device MAC or custom ID
    space_id = Column(Integer, ForeignKey("spaces.id"))
    location_description = Column(String, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    space = relationship("Space", back_populates="devices")
    congestion_history = relationship("CongestionData", back_populates="device")

class CongestionData(Base):
    __tablename__ = "congestion_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("scanner_devices.id"))
    wifi_count = Column(Integer, default=0)
    bt_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    device = relationship("ScannerDevice", back_populates="congestion_history")
