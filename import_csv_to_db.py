import csv
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.models import RawScannerData, ScannerDevice

def import_csv_data(csv_file_path: str):
    db: Session = SessionLocal()
    capacity_cache = {}
    success_count = 0
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            raw_logs = []
            for row in reader:
                device_id = row.get('device_id', '').strip()
                if not device_id:
                    continue
                    
                wifi_count = int(row.get('wifi_count', 0))
                bt_count = int(row.get('bt_count', 0))
                
                # 타임스탬프 파싱 (형식: YYYY-MM-DD HH:MM:SS)
                timestamp_str = row.get('timestamp', '').strip()
                if timestamp_str:
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        try:
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            timestamp = datetime.now()
                else:
                    timestamp = datetime.now()

                # CSV에 count와 congestion_level이 이미 있다면 그대로 사용, 없다면 계산
                count_str = row.get('count', '').strip()
                congestion_str = row.get('congestion_level', '').strip()
                
                if count_str and congestion_str:
                    calculated_count = float(count_str)
                    congestion_level = int(congestion_str)
                else:
                    # 값이 없을 경우 직접 산출
                    if device_id not in capacity_cache:
                        device = db.query(ScannerDevice).filter(ScannerDevice.id == device_id).first()
                        if device and device.space:
                            capacity_cache[device_id] = device.space.max_capacity
                        else:
                            print(f"경고: {device_id} 기기나 해당 장소가 존재하지 않습니다. 건너뜁니다.")
                            continue
                    
                    max_capacity = capacity_cache[device_id]
                    hybrid_count = max(bt_count * 0.8, (wifi_count * 0.7) + (bt_count * 0.3))
                    calculated_count = int(round(hybrid_count))

                    if max_capacity > 0:
                        congestion_level = max(0, min(100, round((calculated_count / max_capacity) * 100)))
                    else:
                        congestion_level = 0
                
                # 로그 객체 생성 (기존 id는 충돌 방지를 위해 무시하고 자동 생성에 맡깁니다)
                log = RawScannerData(
                    device_id=device_id,
                    wifi_count=wifi_count,
                    bt_count=bt_count,
                    count=calculated_count,
                    congestion_level=congestion_level,
                    timestamp=timestamp
                )
                raw_logs.append(log)
            
            if raw_logs:
                db.add_all(raw_logs)
                db.commit()
                success_count = len(raw_logs)
                
        print(f"✅ 총 {success_count}개의 데이터가 성공적으로 추가되었습니다!")

    except Exception as e:
        db.rollback()
        print(f"❌ 데이터 삽입 중 오류가 발생했습니다: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python import_csv_to_db.py <csv파일경로>")
    else:
        import_csv_data(sys.argv[1])
