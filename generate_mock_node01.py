import csv
import random
from datetime import datetime, timedelta

def generate_node01_data():
    template_records = []
    
    # 1. ESP_NODE_03의 6월 5일 데이터를 시계열 패턴(증감 유형) 템플릿으로 사용
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_03' and '2026-06-05' in row['timestamp']:
                template_records.append(row)
                
    if not template_records:
        print("템플릿 데이터가 없습니다.")
        return

    # 분석 결과: ESP_NODE_01 평균 (WiFi 20.9, BT 52.5) / ESP_NODE_03 6.5평균 (WiFi 31.3, BT 19.6)
    # 스케일링 비율 계산
    wifi_scale = 20.94 / 31.3  # 약 0.67
    bt_scale = 52.50 / 19.6    # 약 2.68

    start_date = datetime(2026, 5, 28)
    target_dates = [start_date + timedelta(days=i) for i in range(7)]
    
    output_records = []
    
    for target_date in target_dates:
        is_weekend = target_date.weekday() >= 5  # 5: 토요일, 6: 일요일
        
        for record in template_records:
            try:
                orig_time = datetime.strptime(record['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
            new_timestamp = orig_time.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            
            orig_wifi = int(record['wifi_count'])
            orig_bt = int(record['bt_count'])
            
            # 기준값 스케일링 적용 + 무작위 편차
            variation = random.uniform(0.8, 1.2)
            new_wifi = int((orig_wifi * wifi_scale) * variation)
            new_bt = int((orig_bt * bt_scale) * variation)
            
            # 주말 50% 하향 페널티
            if is_weekend:
                new_wifi = int(new_wifi * 0.5)
                new_bt = int(new_bt * 0.5)
                
            output_records.append({
                'device_id': 'ESP_NODE_01',
                'wifi_count': max(0, new_wifi),
                'bt_count': max(0, new_bt),
                'timestamp': new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    # sample_data.csv에 "추가(Append)"
    with open('sample_data.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['device_id', 'wifi_count', 'bt_count', 'timestamp'])
        writer.writerows(output_records)
        
    print(f"ESP_NODE_01 가상 데이터 생성 및 추가 완료: 총 {len(output_records)}건")

if __name__ == '__main__':
    generate_node01_data()
