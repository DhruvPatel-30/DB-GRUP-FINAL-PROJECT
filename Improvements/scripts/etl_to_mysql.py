import os
import pandas as pd
import pymysql
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from monitoring_utils import record_db_metrics

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")
DATASET_URL = os.getenv("DATASET_URL", "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet")

CHUNK_SIZE = 50000

def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def download_data():
    print(f"Downloading dataset from {DATASET_URL}...")
    os.makedirs("data", exist_ok=True)
    
    if DATASET_URL.endswith('.parquet'):
        file_path = "data/taxi_data.parquet"
    else:
        file_path = "data/taxi_data.csv"
    
    r = requests.get(DATASET_URL, stream=True)
    r.raise_for_status()
    
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("Download complete.")
    return file_path

def clean_chunk(df):
    column_mapping = {
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
    }
    
    df = df.rename(columns=column_mapping)
    
    required_cols = [
        "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
        "trip_distance", "rate_code_id", "store_and_fwd_flag", "pu_location_id",
        "do_location_id", "payment_type", "fare_amount", "extra", "mta_tax",
        "tip_amount", "tolls_amount", "improvement_surcharge", "total_amount",
        "congestion_surcharge", "airport_fee"
    ]
    
    available_cols = [col for col in required_cols if col in df.columns]
    df = df[available_cols]
    
    for col in required_cols:
        if col not in df.columns:
            if col == "store_and_fwd_flag":
                df[col] = "N"
            elif col == "vendor_id":
                df[col] = "1"
            else:
                df[col] = 0
    
    df = df[required_cols]
    df = df.fillna(0)
    df["vendor_id"] = df["vendor_id"].astype(str)
    
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
            try:
                cur.execute(sql, tuple(row))
            except Exception as e:
                print(f"Error inserting row: {e}")
                continue

def record_etl_metrics(conn, rows, duration):
    sql = """
        INSERT INTO etl_metrics (rows_loaded, duration_seconds, created_at)
        VALUES (%s, %s, NOW())
    """
    with conn.cursor() as cur:
        cur.execute(sql, (rows, duration))

def main():
    overall_start = time.time()
    conn = get_mysql_conn()
    file_path = download_data()

    total_rows = 0
    error_count = 0

    try:
        if file_path.endswith('.parquet'):
            df_full = pd.read_parquet(file_path)
            for i in range(0, len(df_full), CHUNK_SIZE):
                chunk_start = time.time()
                chunk = df_full.iloc[i:i+CHUNK_SIZE]
                print(f"Processing chunk {i//CHUNK_SIZE + 1}...")
                clean_df = clean_chunk(chunk)
                insert_chunk(conn, clean_df)
                total_rows += len(clean_df)
                
                # Record metrics for this chunk
                record_db_metrics("mysql", "etl_chunk", chunk_start, error_count=0)
                
                print(f"Inserted {len(clean_df)} rows. Total: {total_rows}")
        else:
            for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
                chunk_start = time.time()
                print(f"Processing chunk...")
                clean_df = clean_chunk(chunk)
                insert_chunk(conn, clean_df)
                total_rows += len(clean_df)
                
                # Record metrics for this chunk
                record_db_metrics("mysql", "etl_chunk", chunk_start, error_count=0)
                
                print(f"Inserted {len(clean_df)} rows. Total: {total_rows}")
    
    except Exception as e:
        error_count += 1
        print(f"Error during ETL: {e}")
        raise

    duration = round(time.time() - overall_start, 2)
    print(f"ETL complete. Total rows: {total_rows} | Time: {duration}s")

    record_etl_metrics(conn, total_rows, duration)
    
    # Record overall ETL metrics
    record_db_metrics("mysql", "etl_complete", overall_start, error_count=error_count)
    
    conn.close()

if __name__ == "__main__":
    main()