import csv
import random
from datetime import datetime, timedelta

def generate_node02_data():
    template_records = []
    
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_03' and '2026-06-05' in row['timestamp']:
                template_records.append(row)

    # 1. 공간 크기가 Node04(수용인원 60)와 비슷하거나 약간 작음 (수용인원 40)
    # 2. Node01처럼 BT 비율이 높음
    # Node03 템플릿(점심 피크 WiFi 63, BT 52)을 기반으로 스케일링
    # 하이브리드 점수가 30~40 대가 나오도록 스케일 낮춤
    wifi_scale = 0.4  # 피크 시 약 25
    bt_scale = 1.0    # 피크 시 약 52
    
    start_date = datetime(2026, 5, 28)
    target_dates = [start_date + timedelta(days=i) for i in range(7)]
    
    output_records = []
    
    for target_date in target_dates:
        is_weekend = target_date.weekday() >= 5
        
        for record in template_records:
            try:
                orig_time = datetime.strptime(record['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
            new_timestamp = orig_time.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            
            orig_wifi = int(record['wifi_count'])
            orig_bt = int(record['bt_count'])
            variation = random.uniform(0.8, 1.2)
            
            # 스케일 적용
            new_wifi = int((orig_wifi * wifi_scale) * variation)
            new_bt = int((orig_bt * bt_scale) * variation)
            
            # 주간(09시 ~ 18시)에는 유동인구가 항상 있도록 소폭의 하한선 보정
            # 밤이나 새벽에는 원본 템플릿(0에 수렴)을 따라 자연스럽게 없어짐
            if 9 <= new_timestamp.hour <= 18:
                if new_wifi < 5: new_wifi = random.randint(5, 8)
                if new_bt < 8: new_bt = random.randint(8, 12)
            
            # 주말 50% 페널티
            if is_weekend:
                new_wifi = int(new_wifi * 0.5)
                new_bt = int(new_bt * 0.5)
                
            output_records.append({
                'device_id': 'ESP_NODE_02',
                'wifi_count': max(0, new_wifi),
                'bt_count': max(0, new_bt),
                'timestamp': new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    with open('sample_data.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['device_id', 'wifi_count', 'bt_count', 'timestamp'])
        writer.writerows(output_records)
        
    print(f"ESP_NODE_02 가상 데이터 생성 및 추가 완료: 총 {len(output_records)}건")

if __name__ == '__main__':
    generate_node02_data()
