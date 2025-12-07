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

# 🚀 Increased chunk size for faster inserts
CHUNK_SIZE = 20000


# -----------------------------
#  Database Connection
# -----------------------------
def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )


# -----------------------------
#  Download Data
# -----------------------------
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


# -----------------------------
#  Data Cleaning
# -----------------------------
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

    # Keep only columns that exist
    available_cols = [col for col in required_cols if col in df.columns]
    df = df[available_cols]

    # Add missing required columns
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



# -----------------------------
#  SUPER FAST BULK INSERT
# -----------------------------
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

    # Convert dataframe rows → list of tuples ONCE
    data = [tuple(row) for row in df.itertuples(index=False, name=None)]

    with conn.cursor() as cur:
        cur.executemany(sql, data)



# -----------------------------
#  Record ETL Metrics
# -----------------------------
def record_etl_metrics(conn, rows, duration):
    sql = """
        INSERT INTO etl_metrics (rows_loaded, duration_seconds, created_at)
        VALUES (%s, %s, NOW())
    """
    with conn.cursor() as cur:
        cur.execute(sql, (rows, duration))



# -----------------------------
#  MAIN ETL PIPELINE
# -----------------------------
def main():
    overall_start = time.time()
    conn = get_mysql_conn()
    file_path = download_data()

    total_rows = 0
    error_count = 0

    try:
        if file_path.endswith('.parquet'):
            df_full = pd.read_parquet(file_path)
            chunks = range(0, len(df_full), CHUNK_SIZE)

            for idx, i in enumerate(chunks, start=1):
                chunk_start = time.time()

                print(f"Processing chunk {idx}...")

                chunk = df_full.iloc[i:i+CHUNK_SIZE]
                clean_df = clean_chunk(chunk)

                insert_chunk(conn, clean_df)

                total_rows += len(clean_df)

                # Monitoring
                record_db_metrics("mysql", "etl_chunk", chunk_start, error_count=0)

                print(f"Inserted {len(clean_df)} rows. Total: {total_rows}")

        else:
            for idx, chunk in enumerate(pd.read_csv(file_path, chunksize=CHUNK_SIZE), start=1):
                chunk_start = time.time()

                print(f"Processing chunk {idx}...")

                clean_df = clean_chunk(chunk)

                insert_chunk(conn, clean_df)

                total_rows += len(clean_df)

                record_db_metrics("mysql", "etl_chunk", chunk_start, error_count=0)

                print(f"Inserted {len(clean_df)} rows. Total: {total_rows}")

    except Exception as e:
        error_count += 1
        print(f"Error during ETL: {e}")
        raise

    duration = round(time.time() - overall_start, 2)
    print(f"ETL complete. Total rows: {total_rows} | Time: {duration}s")

    record_etl_metrics(conn, total_rows, duration)

    # Final ETL Monitoring
    record_db_metrics("mysql", "etl_complete", overall_start, error_count=error_count)

    conn.close()



if __name__ == "__main__":
    main()