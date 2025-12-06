import os
import pymysql
import time
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
from monitoring_utils import record_db_metrics

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB_NAME", "nyc_taxi_db")

def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def sync_data():
    start_time = time.time()
    error_count = 0
    
    print("Connecting to MySQL...")
    conn = get_mysql_conn()
    
    print("Connecting to MongoDB...")
    mongo = MongoClient(MONGO_URI)
    db = mongo[MONGO_DB]
    col = db["taxi_trips"]

    print("Fetching data from MySQL...")
    fetch_start = time.time()
    
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM taxi_trips LIMIT 100000")
        rows = cur.fetchall()
    
    record_db_metrics("mysql", "sync_fetch", fetch_start, error_count=0)

    print(f"Syncing {len(rows)} records to MongoDB...")
    sync_start = time.time()
    
    ops = []
    for r in rows:
        try:
            for key, val in r.items():
                if hasattr(val, 'isoformat'):
                    r[key] = val.isoformat()
            
            ops.append(UpdateOne({"trip_id": r["trip_id"]}, {"$set": r}, upsert=True))
        except Exception as e:
            error_count += 1
            print(f"Error preparing record: {e}")

    if ops:
        try:
            result = col.bulk_write(ops)
            print(f" Synced {len(ops)} documents → MongoDB")
            print(f"   Inserted: {result.upserted_count}, Modified: {result.modified_count}")
        except Exception as e:
            error_count += 1
            print(f"Error during bulk write: {e}")
    else:
        print("No data to sync")
    
    record_db_metrics("mongodb", "sync_write", sync_start, error_count=error_count)
    record_db_metrics("mysql", "sync_complete", start_time, error_count=error_count)
    
    conn.close()
    mongo.close()

if __name__ == "__main__":
    sync_data()