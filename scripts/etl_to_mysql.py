import os
import pandas as pd
import pymysql
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DATABASE")
DATASET_URL = os.getenv("DATASET_URL")

CHUNK_SIZE = 50000  # 50k rows per chunk

def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def download_csv():
    print("Downloading dataset...")
    r = requests.get(DATASET_URL)
    csv_path = "data/taxi_data.csv"
    os.makedirs("data", exist_ok=True)
    with open(csv_path, "wb") as f:
        f.write(r.content)
    print("Download complete.")
    return csv_path

def clean_chunk(df):
    # Basic cleaning for NYC Taxi dataset
    df = df.rename(columns={
        "VendorID": "vendor_id",
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "passenger_count": "passenger_count",
        "trip_distance": "trip_distance",
        "RatecodeID": "rate_code_id",
        "store_and_fwd_flag": "store_and_fwd_flag",
        "PULocationID": "pu_location_id",
        "DOLocationID": "do_location_id",
        "payment_type": "payment_type",
        "fare_amount": "fare_amount",
        "extra": "extra",
        "mta_tax": "mta_tax",
        "tip_amount": "tip_amount",
        "tolls_amount": "tolls_amount",
        "improvement_surcharge": "improvement_surcharge",
        "total_amount": "total_amount",
        "congestion_surcharge": "congestion_surcharge",
        "Airport_fee": "airport_fee"
    })

    df = df[[
        "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
        "trip_distance", "rate_code_id", "store_and_fwd_flag", "pu_location_id",
        "do_location_id", "payment_type", "fare_amount", "extra", "mta_tax",
        "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount",
        "congestion_surcharge", "airport_fee"
    ]]

    df = df.fillna(0)
    return df

def insert_chunk(conn, df):
    sql = """
        INSERT INTO taxi_trips (
            vendor_id, pickup_datetime, dropoff_datetime, passenger_count,
            trip_distance, rate_code_id, store_and_fwd_flag, pu_location_id,
            do_location_id, payment_type, fare_amount, extra, mta_tax,
            tip_amount, tolls_amount, improvement_surcharge, total_amount,
            congestion_surcharge, airport_fee
        ) VALUES (
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
        )
    """

    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(sql, tuple(row))

def record_metrics(conn, rows, duration):
    sql = """
        INSERT INTO etl_metrics (rows_loaded, duration_seconds, created_at)
        VALUES (%s, %s, NOW())
    """
    with conn.cursor() as cur:
        cur.execute(sql, (rows, duration))

def main():
    conn = get_mysql_conn()
    csv_path = download_csv()

    start = time.time()
    total_rows = 0

    for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE):
        print(f"Processing chunk...")
        clean_df = clean_chunk(chunk)
        insert_chunk(conn, clean_df)
        total_rows += len(clean_df)
        print(f"Inserted {len(clean_df)} rows.")

    duration = round(time.time() - start, 2)
    print(f"ETL complete. Total rows: {total_rows} | Time: {duration}s")

    record_metrics(conn, total_rows, duration)

if __name__ == "__main__":
    main()
