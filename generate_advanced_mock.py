import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict

def generate_advanced_mock():
    # 1. 템플릿 데이터 로드
    node03_template = []
    node04_templates = defaultdict(list)
    
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt = datetime.strptime(row['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
                
            if row['device_id'] == 'ESP_NODE_03' and dt.date() == datetime(2026, 6, 5).date():
                node03_template.append((dt, int(row['wifi_count']), int(row['bt_count'])))
            elif row['device_id'] == 'ESP_NODE_04':
                date_str = dt.strftime('%Y-%m-%d')
                node04_templates[date_str].append((dt, int(row['wifi_count']), int(row['bt_count'])))

    # Node 04 템플릿 매핑
    node04_mapping = {
        '2026-05-28': '2026-06-05',
        '2026-05-29': '2026-06-05',
        '2026-05-30': '2026-06-06',
        '2026-05-31': '2026-06-07',
        '2026-06-01': '2026-06-08',
        '2026-06-02': '2026-06-08',
        '2026-06-03': '2026-06-05'
    }

    start_date = datetime(2026, 5, 28)
    target_dates = [start_date + timedelta(days=i) for i in range(7)]
    
    output_records = []

    for target_date in target_dates:
        # 매일 전체 일정이 조금씩 이동 (-30분 ~ +30분)
        daily_time_shift = timedelta(minutes=random.randint(-30, 30))
        # 매일 전체 유동인구 스케일 (0.85배 ~ 1.15배)
        daily_volume_scale = random.uniform(0.85, 1.15)
        
        is_weekend = target_date.weekday() >= 5
        is_friday = target_date.weekday() == 4
        is_monday = target_date.weekday() == 0

        # === Node 01, 02, 03 생성 ===
        for orig_dt, orig_wifi, orig_bt in node03_template:
            # 5% 확률로 레코드 누락 (도장 찍기 방지)
            if random.random() < 0.05:
                continue

            new_dt = orig_dt.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            shifted_dt = new_dt + daily_time_shift
            
            # 개별 노이즈 (1.0 기준 ±5%)
            record_noise = random.uniform(0.95, 1.05)
            final_scale = daily_volume_scale * record_noise

            # --- Node 03 (원본) ---
            # Node 3은 금요일 밤~월요일 아침 데이터 없음
            skip_node3 = False
            if is_weekend:
                skip_node3 = True
            if is_friday and shifted_dt.time() >= datetime.strptime("19:10:00", "%H:%M:%S").time():
                skip_node3 = True
            if is_monday and shifted_dt.time() <= datetime.strptime("08:36:00", "%H:%M:%S").time():
                skip_node3 = True
                
            if not skip_node3:
                output_records.append({
                    'device_id': 'ESP_NODE_03',
                    'wifi_count': max(0, int(orig_wifi * final_scale)),
                    'bt_count': max(0, int(orig_bt * final_scale)),
                    'timestamp': shifted_dt.strftime('%Y-%m-%d %H:%M:%S')
                })

            # --- Node 01 (고 BT, 저 WiFi) ---
            wifi_01 = orig_wifi * 0.67 * final_scale
            bt_01 = orig_bt * 2.68 * final_scale
            if is_weekend:
                wifi_01 *= 0.5
                bt_01 *= 0.5
            output_records.append({
                'device_id': 'ESP_NODE_01',
                'wifi_count': max(0, int(wifi_01)),
                'bt_count': max(0, int(bt_01)),
                'timestamp': shifted_dt.strftime('%Y-%m-%d %H:%M:%S')
            })

            # --- Node 02 (혼잡한 공간) ---
            wifi_02 = orig_wifi * 0.4 * final_scale
            bt_02 = orig_bt * 1.0 * final_scale
            # 주간 하한선 추가
            if 9 <= shifted_dt.hour <= 18:
                if wifi_02 < 5: wifi_02 = random.randint(5, 8)
                if bt_02 < 8: bt_02 = random.randint(8, 12)
            if is_weekend:
                wifi_02 *= 0.5
                bt_02 *= 0.5
            output_records.append({
                'device_id': 'ESP_NODE_02',
                'wifi_count': max(0, int(wifi_02)),
                'bt_count': max(0, int(bt_02)),
                'timestamp': shifted_dt.strftime('%Y-%m-%d %H:%M:%S')
            })

        # === Node 04 생성 ===
        target_date_str = target_date.strftime('%Y-%m-%d')
        template_date_str = node04_mapping[target_date_str]
        for orig_dt, orig_wifi, orig_bt in node04_templates[template_date_str]:
            if random.random() < 0.05:
                continue
                
            new_dt = orig_dt.replace(year=target_date.year, month=target_date.month, day=target_date.day)
            shifted_dt = new_dt + daily_time_shift
            record_noise = random.uniform(0.95, 1.05)
            final_scale = daily_volume_scale * record_noise

            output_records.append({
                'device_id': 'ESP_NODE_04',
                'wifi_count': max(0, int(orig_wifi * final_scale)),
                'bt_count': max(0, int(orig_bt * final_scale)),
                'timestamp': shifted_dt.strftime('%Y-%m-%d %H:%M:%S')
            })

    # 정렬하여 출력 (시간 순)
    output_records.sort(key=lambda x: x['timestamp'])

    with open('sample_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['device_id', 'wifi_count', 'bt_count', 'timestamp'])
        writer.writeheader()
        writer.writerows(output_records)
        
    print(f"고급 가상 데이터 통합 생성 완료: 총 {len(output_records)}건 저장됨")

if __name__ == '__main__':
    generate_advanced_mock()
