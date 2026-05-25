from app.core.database import SessionLocal, engine, Base
from app.models.models import Space, ScannerDevice, CongestionData, RawScannerData, get_kst_now

# 테이블 생성
Base.metadata.drop_all(bind=engine) # 기존 테이블 삭제 후 재생성 (스키마 변경 반영)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. 공간 생성
    spaces = [
        Space(name="일신관라운지", description="일신관 1층 라운지", low_threshold=15.0, medium_threshold=40.0),
        Space(name="성호관라운지", description="성호관 1층 라운지", low_threshold=10.0, medium_threshold=30.0),
        Space(name="아슐랭", description="학생식당 아슐랭", low_threshold=50.0, medium_threshold=120.0),
        Space(name="학생회관카페", description="학생회관 1층 카페", low_threshold=20.0, medium_threshold=50.0),
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
        result = "보통" # 임계값에 따라 다르지만 예시로 설정
        
        # 현재 상태 저장
        db.add(CongestionData(device_id=device.id, count=count, result=result, timestamp=get_kst_now()))
        
        # 원본 로그 저장
        db.add(RawScannerData(
            device_id=device.id, 
            wifi_count=wifi, 
            bt_count=bt, 
            count=count, 
            result=result, 
            timestamp=get_kst_now()
        ))

    db.commit()
    db.close()
    print("DB 초기화 및 샘플 데이터(공간, 장치, 혼잡도 상태, 로그)가 생성되었습니다.")

if __name__ == "__main__":
    seed_data()
