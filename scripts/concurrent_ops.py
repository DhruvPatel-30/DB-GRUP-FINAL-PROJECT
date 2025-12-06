import threading
import time
import pymysql
import os
from dotenv import load_dotenv
from monitoring_utils import record_db_metrics

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")  # ← FIXED: Was MMYSQL_HOST
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True
    )

def insert_op(thread_id):
    start = time.time()
    conn = get_conn()
    errors = 0
    
    try:
        with conn.cursor() as cur:
            sql = """
            INSERT INTO taxi_trips (vendor_id, pickup_datetime, dropoff_datetime,
            passenger_count, trip_distance, rate_code_id, store_and_fwd_flag,
            pu_location_id, do_location_id, payment_type, fare_amount, extra,
            mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount,
            congestion_surcharge, airport_fee)
            VALUES ('1', NOW(), NOW(), 1, 1.2, 1, 'N', 10, 20, 1, 5.0, 0.5, 0.5, 1.0, 0.0, 0.3, 7.3, 0.0, 0.0)
            """
            for i in range(100):
                cur.execute(sql)
    except Exception as e:
        errors += 1
        print(f"Insert error in thread {thread_id}: {e}")
    
    duration = time.time() - start
    record_db_metrics("mysql", "concurrent_insert", start, error_count=errors)
    print(f"[Thread {thread_id}] Insert completed in {duration:.2f}s (errors: {errors})")
    conn.close()

def update_op(thread_id):
    start = time.time()
    conn = get_conn()
    errors = 0
    
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE taxi_trips SET fare_amount = fare_amount + 0.01 WHERE trip_id % 10 = 0 LIMIT 100")
    except Exception as e:
        errors += 1
        print(f"Update error in thread {thread_id}: {e}")
    
    duration = time.time() - start
    record_db_metrics("mysql", "concurrent_update", start, error_count=errors)
    print(f"[Thread {thread_id}] Update completed in {duration:.2f}s (errors: {errors})")
    conn.close()

def select_op(thread_id):
    start = time.time()
    conn = get_conn()
    errors = 0
    
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt, AVG(fare_amount) as avg_fare FROM taxi_trips")
            result = cur.fetchone()
            print(f"[Thread {thread_id}] Query result: {result}")
    except Exception as e:
        errors += 1
        print(f"Select error in thread {thread_id}: {e}")
    
    duration = time.time() - start
    record_db_metrics("mysql", "concurrent_select", start, error_count=errors)
    print(f"[Thread {thread_id}] Select completed in {duration:.2f}s (errors: {errors})")
    conn.close()

def main():
    print("Starting concurrent operations test...")
    print("="*60)
    
    start_time = time.time()
    threads = []
    
    operations = [
        (insert_op, 3),
        (update_op, 2),
        (select_op, 5),
    ]
    
    thread_id = 0
    for func, count in operations:
        for _ in range(count):
            thread_id += 1
            t = threading.Thread(target=func, args=(thread_id,))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()

    total_duration = time.time() - start_time
    
    # Record overall concurrent ops metrics
    record_db_metrics("mysql", "concurrent_complete", start_time, error_count=0)
    
    print("="*60)
    print(f"✅ All concurrent operations complete in {total_duration:.2f}s")
    print(f"   Total threads: {len(threads)}")
    
    # Print metrics summary
    from monitoring_utils import print_metrics_summary
    print_metrics_summary()

if __name__ == "__main__":
    main()