from app.core.database import SessionLocal, engine, Base
from app.models.models import Space, ScannerDevice

# 테이블 생성
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # 1. 공간 생성
    ilshinlounge = Space(name="일신관라운지", description="일신관라운지어디")
    sungholounge = Space(name="성호관라운지", description="성호관라운지어디")
    studentcafeteria = Space(name="아슐랭", description="아슐랭어디")
    studentcafe = Space(name="학생회관카페", description="학생회관카페어디")

    db.add(ilshinlounge)
    db.add(sungholounge)
    db.add(studentcafeteria)
    db.add(studentcafe)

    db.commit() # ID 생성을 위해 커밋
    
    # 2. 장치와 공간 연결
    # 장치는 각 공간별로 하나씩만 있다고 가정
    device1 = ScannerDevice(id="ESP_NODE_01", space_id=ilshinlounge.id, location_description="일신라운지")
    device2 = ScannerDevice(id="ESP_NODE_02", space_id=sungholounge.id, location_description="성호라운지")
    device3 = ScannerDevice(id="ESP_NODE_03", space_id=studentcafeteria.id, location_description="아슐랭")
    device4 = ScannerDevice(id="ESP_NODE_04", space_id=studentcafe.id, location_description="학생식당카페")

    db.add(device1)
    db.add(device2)
    db.add(device3)
    db.add(device4)
    db.commit()
    db.close()
    print("초기 데이터가 성공적으로 생성되었습니다.")

if __name__ == "__main__":
    seed_data()
