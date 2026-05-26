from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from app.core.database import Base

def get_kst_now():
    """한국 표준시(KST)를 반환합니다."""
    return datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)

class Space(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # 최대 수용 인원
    max_capacity = Column(Integer, default=50)

    # Relationship
    devices = relationship("ScannerDevice", back_populates="space")

class ScannerDevice(Base):
    __tablename__ = "scanner_devices"

    id = Column(String, primary_key=True, index=True)
    space_id = Column(Integer, ForeignKey("spaces.id"))
    location_description = Column(String, nullable=True)
    last_seen = Column(DateTime, default=get_kst_now, onupdate=get_kst_now)

    # Relationships
    space = relationship("Space", back_populates="devices")
    congestion_history = relationship("CongestionData", back_populates="device")
    raw_logs = relationship("RawScannerData", back_populates="device")

class CongestionData(Base):
    __tablename__ = "congestion_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("scanner_devices.id"), unique=True, index=True, nullable=False)
    count = Column(Float, default=0.0)
    congestion_level = Column(Integer, default=0) # max_capacity 대비 백분율 (0-100)
    timestamp = Column(DateTime, default=get_kst_now)

    # Relationship
    device = relationship("ScannerDevice", back_populates="congestion_history")

class RawScannerData(Base):
    """센서로부터 받은 원본 데이터와 계산 결과를 기록하는 로그 테이블"""
    __tablename__ = "raw_scanner_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("scanner_devices.id"), index=True, nullable=False)
    wifi_count = Column(Integer, nullable=False)
    bt_count = Column(Integer, nullable=False)
    count = Column(Float, nullable=True)  # 계산된 점수
    congestion_level = Column(Integer, nullable=True) # 판정 결과 (백분율)
    timestamp = Column(DateTime, default=get_kst_now)


    # Relationship
    device = relationship("ScannerDevice", back_populates="raw_logs")
