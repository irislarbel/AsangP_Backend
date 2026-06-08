import csv
import random
from datetime import datetime, timedelta

def generate_mock_data():
    template_records = []
    
    # 1. 6월 5일(가장 데이터가 많은 날)을 템플릿으로 추출
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_03' and '2026-06-05' in row['timestamp']:
                template_records.append(row)
                
    if not template_records:
        print("6월 5일 템플릿 데이터가 없습니다.")
        return

    # 목표 생성 날짜: 2026-05-28 ~ 2026-06-03
    start_date = datetime(2026, 5, 28)
    target_dates = [start_date + timedelta(days=i) for i in range(7)]
    
    output_records = []
    
    for target_date in target_dates:
        is_weekend = target_date.weekday() >= 5  # 5: 토요일, 6: 일요일
        
        for record in template_records:
            # 시간 파싱
            try:
                orig_time = datetime.strptime(record['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
            # 타임스탬프를 target_date로 변경
            new_timestamp = orig_time.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            
            # 원본 수치
            orig_wifi = int(record['wifi_count'])
            orig_bt = int(record['bt_count'])
            
            # 편차 적용 (평일: -20% ~ +20%)
            variation = random.uniform(0.8, 1.2)
            new_wifi = int(orig_wifi * variation)
            new_bt = int(orig_bt * variation)
            
            # 주말 페널티 (50%)
            if is_weekend:
                new_wifi = int(new_wifi * 0.5)
                new_bt = int(new_bt * 0.5)
                
            output_records.append({
                'device_id': 'ESP_NODE_03',
                'wifi_count': max(0, new_wifi),
                'bt_count': max(0, new_bt),
                'timestamp': new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    # sample_data.csv에 저장 (헤더: device_id,wifi_count,bt_count,timestamp)
    # count와 congestion_level은 import 스크립트가 계산하도록 남겨둠
    with open('sample_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['device_id', 'wifi_count', 'bt_count', 'timestamp'])
        writer.writeheader()
        writer.writerows(output_records)
        
    print(f"가상 데이터 생성 완료: 총 {len(output_records)}건 저장됨 (sample_data.csv)")

if __name__ == '__main__':
    generate_mock_data()
