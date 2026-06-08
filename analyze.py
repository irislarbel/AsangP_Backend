import csv
from collections import defaultdict
import statistics

def check_node01():
    stats = {'wifi': [], 'bt': []}
    
    with open('ScannerRawLog_2026-06-08_07-32-38.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['device_id'] == 'ESP_NODE_01':
                try:
                    stats['wifi'].append(int(row['wifi_count']))
                    stats['bt'].append(int(row['bt_count']))
                except:
                    pass
            
    if not stats['wifi']:
        print("ESP_NODE_01 데이터가 없습니다.")
        return
        
    avg_wifi = statistics.mean(stats['wifi'])
    avg_bt = statistics.mean(stats['bt'])
    
    print(f"ESP_NODE_01 총 데이터 건수: {len(stats['wifi'])}")
    print(f"ESP_NODE_01 평균 WiFi: {avg_wifi:.2f}")
    print(f"ESP_NODE_01 평균 BT: {avg_bt:.2f}")

if __name__ == '__main__':
    check_node01()
