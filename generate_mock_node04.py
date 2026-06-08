import csv
import random
from datetime import datetime
from collections import defaultdict

def generate_node04_data():
    template_data = defaultdict(list)
    
    # 1. 원본 데이터 읽어서 날짜별로 템플릿 저장
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_04':
                try:
                    date_str = row['timestamp'].split(' ')[0]
                    template_data[date_str].append(row)
                except:
                    pass

    # 2. 매핑 룰: 6월 4일(목)은 사용자 요청으로 배제, 목/화/수는 월/금으로 대체
    mapping = {
        '2026-05-28': '2026-06-05', # 목 -> 금
        '2026-05-29': '2026-06-05', # 금 -> 금
        '2026-05-30': '2026-06-06', # 토 -> 토
        '2026-05-31': '2026-06-07', # 일 -> 일
        '2026-06-01': '2026-06-08', # 월 -> 월
        '2026-06-02': '2026-06-08', # 화 -> 월
        '2026-06-03': '2026-06-05'  # 수 -> 금
    }
    
    output_records = []
    
    for target_date_str, template_date_str in mapping.items():
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        template_records = template_data[template_date_str]
        
        for record in template_records:
            try:
                orig_time = datetime.strptime(record['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
            new_timestamp = orig_time.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            orig_wifi = int(record['wifi_count'])
            orig_bt = int(record['bt_count'])
            
            # 주말/평일 모두 원본 요일(혹은 대체 평일) 데이터를 그대로 쓰므로
            # 추가적인 주말 50% 하향 페널티 없이 ±20% 무작위 편차만 적용
            variation = random.uniform(0.8, 1.2)
            new_wifi = int(orig_wifi * variation)
            new_bt = int(orig_bt * variation)
                
            output_records.append({
                'device_id': 'ESP_NODE_04',
                'wifi_count': max(0, new_wifi),
                'bt_count': max(0, new_bt),
                'timestamp': new_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

    # 3. 기존 ESP_NODE_03 데이터가 있는 sample_data.csv에 추가(Append)
    with open('sample_data.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['device_id', 'wifi_count', 'bt_count', 'timestamp'])
        # append 모드이므로 헤더는 작성하지 않음
        writer.writerows(output_records)
        
    print(f"ESP_NODE_04 가상 데이터 추가 완료: 총 {len(output_records)}건")

if __name__ == '__main__':
    generate_node04_data()
