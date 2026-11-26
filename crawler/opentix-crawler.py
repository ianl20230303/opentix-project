import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import pymysql

# 資料庫連線設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'opentix_db',
    'charset': 'utf8mb4'
}

def save_to_mysql(records):
    """將資料寫入歷史表，並覆蓋更新最新票況表"""
    if not records:
        return
        
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    sql_history = """
        INSERT INTO opentix_tickets_history (EVENT_NAME, EVENT_TIME, REMAIN_SEATS, PRICE)
        VALUES (%s, %s, %s, %s)
    """
    sql_latest = """
        INSERT INTO opentix_tickets_latest (EVENT_NAME, EVENT_TIME, REMAIN_SEATS, PRICE)
        VALUES (%s, %s, %s, %s)
    """
    
    try:
        cursor.executemany(sql_history, records)
        cursor.execute("DELETE FROM opentix_tickets_latest")
        cursor.executemany(sql_latest, records)
        conn.commit()
        print(f"資料庫更新完成，共寫入 {len(records)} 筆資料")
    except Exception as e:
        conn.rollback()
        print(f"資料庫寫入失敗：{e}")
    finally:
        cursor.close()
        conn.close()

# 初始化 HTTP Session 與請求標頭
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Referer': 'https://www.opentix.life/'
}
session = requests.Session()
session.headers.update(headers)

def fetch_program_tickets(prog):
    """取得單一節目的各場次與票區資訊"""
    prog_id = prog['id']
    prog_name = prog['name']
    detail_url = f'https://csm.api.opentix.life/programs/{prog_id}'
    prog_records = []
    
    try:
        res_detail = session.get(detail_url, timeout=10)
        if res_detail.status_code == 200:
            detail_data = json.loads(res_detail.text).get('result', {})
            for venue in detail_data.get('eventVenues', []):
                for event in venue.get('events', []):
                    start_ts = event.get('startDateTime')
                    event_time_str = datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d %H:%M:%S') if start_ts else '未定'
                    
                    for sections in event.get('groupSections', {}).values():
                        for sec in sections:
                            price = sec.get('price', 0)
                            remain_seats = sec.get('quantity', {}).get('remainingQuantity', 0)
                            prog_records.append((prog_name, event_time_str, remain_seats, price))
        else:
            print(f"[{prog_name}] 請求失敗 (HTTP {res_detail.status_code})")
    except Exception as e:
        print(f"[{prog_name}] 爬取異常：{e}")
        
    time.sleep(0.15)
    return prog_records

if __name__ == '__main__':
    start_time = time.time()
    page = 1
    row_count = 50
    all_programs = []

    # 1. 取得全站節目清單
    print("開始收集節目清單...")
    while True:
        list_url = f'https://csm.api.opentix.life/programs?page={page}&rowCount={row_count}'
        res_list = session.get(list_url, timeout=10)
        
        if res_list.status_code != 200:
            print(f"第 {page} 頁清單讀取失敗 (HTTP {res_list.status_code})")
            break
            
        result = json.loads(res_list.text).get('result', {})
        programs = result.get('data', [])
        if not programs:
            break
            
        all_programs.extend(programs)
        print(f"第 {page} 頁讀取完成，累計 {len(all_programs)} 檔節目")
        
        if not result.get('nextPage'):
            break
        page += 1
        time.sleep(0.2)

    # 2. 多執行緒爬取各節目詳細票況
    print(f"\n開始爬取 {len(all_programs)} 檔節目票況...")
    all_records = []
    
    if all_programs:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_program_tickets, prog) for prog in all_programs]
            
            for idx, future in enumerate(as_completed(futures), 1):
                all_records.extend(future.result())
                if idx % 50 == 0 or idx == len(all_programs):
                    print(f"爬取進度：{idx}/{len(all_programs)}")

    elapsed = time.time() - start_time
    print(f"\n爬取結束，總耗時 {elapsed:.2f} 秒，共取得 {len(all_records)} 筆票區資料")

    # 3. 寫入 MySQL 資料庫
    save_to_mysql(all_records)