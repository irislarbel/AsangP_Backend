from app.core.database import SessionLocal, engine, Base
from app.models.models import Space, ScannerDevice

# 테이블 생성
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 이미 데이터가 있는지 확인
    if db.query(Space).first():
        print("이미 데이터가 존재합니다. 시딩을 취소합니다.")
        db.close()
        return

    # 1. 공간 생성 (임계값 추가)
    spaces = [
        Space(name="일신관라운지", description="일신관 1층 라운지", low_threshold=15.0, medium_threshold=40.0),
        Space(name="성호관라운지", description="성호관 1층 라운지", low_threshold=10.0, medium_threshold=30.0),
        Space(name="아슐랭", description="학생식당 아슐랭", low_threshold=50.0, medium_threshold=120.0),
        Space(name="학생회관카페", description="학생회관 1층 카페", low_threshold=20.0, medium_threshold=50.0),
    ]

    for space in spaces:
        db.add(space)

    db.commit() # ID 생성을 위해 커밋
    
    # 2. 장치와 공간 연결
    devices = [
        ScannerDevice(id="ESP_NODE_01", space_id=spaces[0].id, location_description="일신라운지 입구"),
        ScannerDevice(id="ESP_NODE_02", space_id=spaces[1].id, location_description="성호라운지 벽면"),
        ScannerDevice(id="ESP_NODE_03", space_id=spaces[2].id, location_description="아슐랭 기둥"),
        ScannerDevice(id="ESP_NODE_04", space_id=spaces[3].id, location_description="카페 카운터 옆"),
    ]

    for device in devices:
        db.add(device)
    
    db.commit()
    db.close()
    print("초기 데이터(공간 4개, 장치 4개)가 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    seed_data()
