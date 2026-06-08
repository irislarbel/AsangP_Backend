import csv
from datetime import datetime

def analyze_node3_weekend():
    friday_last = None
    monday_first = None
    
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_03':
                try:
                    dt = datetime.strptime(row['timestamp'].split('.')[0], '%Y-%m-%d %H:%M:%S')
                    # 6월 5일(금)의 마지막 시간
                    if dt.date() == datetime(2026, 6, 5).date():
                        if friday_last is None or dt > friday_last:
                            friday_last = dt
                    # 6월 8일(월)의 첫 시간
                    elif dt.date() == datetime(2026, 6, 8).date():
                        if monday_first is None or dt < monday_first:
                            monday_first = dt
                except Exception as e:
                    pass
                    
    print(f"Node 03 금요일(6/5) 마지막 기록 시간: {friday_last}")
    print(f"Node 03 월요일(6/8) 첫 기록 시간: {monday_first}")

if __name__ == '__main__':
    analyze_node3_weekend()
