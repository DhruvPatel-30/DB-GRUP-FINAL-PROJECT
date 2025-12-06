import threading
import time
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DATABASE")

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True
    )

def insert_op():
    conn = get_conn()
    with conn.cursor() as cur:
        sql = """
        INSERT INTO taxi_trips (vendor_id, pickup_datetime, dropoff_datetime,
        passenger_count, trip_distance, rate_code_id, store_and_fwd_flag,
        pu_location_id, do_location_id, payment_type, fare_amount, extra,
        mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount,
        congestion_surcharge, airport_fee)
        VALUES ('1', NOW(), NOW(), 1, 1.2, 1, 'N', 10, 20, 1, 5.0, 0.5, 0.5, 1.0, 0.0, 0.3, 7.3, 0.0, 0.0)
        """
        cur.execute(sql)
    print("Insert thread done.")

def update_op():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("UPDATE taxi_trips SET fare_amount = fare_amount + 1 LIMIT 10")
    print("Update thread done.")

def select_op():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM taxi_trips")
        print("Select count:", cur.fetchone())

def main():
    threads = []
    funcs = [insert_op, update_op, select_op]

    for f in funcs:
        t = threading.Thread(target=f)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("All concurrent operations complete.")

if __name__ == "__main__":
    main()
