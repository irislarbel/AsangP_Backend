from app.core.database import SessionLocal, engine, Base
from app.models.models import Space, ScannerDevice, CongestionData, RawScannerData, get_kst_now

def seed_data():
    # 주의: 아래 코드는 모든 기존 데이터를 삭제합니다. 초기 개발 환경에서만 사용하세요.
    # 운영 환경에서는 Alembic 등을 통한 마이그레이션 권장.
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 1. 공간 생성
    spaces = [
        Space(name="일신관라운지", description="일신관 1층 라운지", max_capacity=50),
        Space(name="성호관라운지", description="성호관 1층 라운지", max_capacity=40),
        Space(name="아슐랭", description="학생식당 아슐랭", max_capacity=150),
        Space(name="학생회관카페", description="학생회관 1층 카페", max_capacity=60),
    ]

    for space in spaces:
        db.add(space)

    db.commit() 
    
    # 2. 장치 생성
    devices = [
        ScannerDevice(id="ESP_NODE_01", space_id=spaces[0].id, location_description="일신라운지 입구"),
        ScannerDevice(id="ESP_NODE_02", space_id=spaces[1].id, location_description="성호라운지 벽면"),
        ScannerDevice(id="ESP_NODE_03", space_id=spaces[2].id, location_description="아슐랭 기둥"),
        ScannerDevice(id="ESP_NODE_04", space_id=spaces[3].id, location_description="카페 카운터 옆"),
    ]

    for device in devices:
        db.add(device)
    
    db.commit()

    # 3. 초기 혼잡도 데이터 및 로그 생성 (테스트용)
    for device in devices:
        # 가상의 데이터 (WiFi 20, BT 10 -> count: 25.0)
        wifi, bt = 20, 10
        count = wifi + (bt * 0.5)
        
        # 공간의 max_capacity를 찾아서 백분율 계산
        space = next(s for s in spaces if s.id == device.space_id)
        congestion_level = min(100, round((count / space.max_capacity) * 100))
        
        # 현재 상태 저장
        db.add(CongestionData(device_id=device.id, count=count, congestion_level=congestion_level, timestamp=get_kst_now()))
        
        # 원본 로그 저장
        db.add(RawScannerData(
            device_id=device.id, 
            wifi_count=wifi, 
            bt_count=bt, 
            count=count, 
            congestion_level=congestion_level, 
            timestamp=get_kst_now()
        ))

    db.commit()
    db.close()
    print("DB 초기화 및 샘플 데이터(공간, 장치, 혼잡도 상태, 로그)가 생성되었습니다.")

if __name__ == "__main__":
    seed_data()
