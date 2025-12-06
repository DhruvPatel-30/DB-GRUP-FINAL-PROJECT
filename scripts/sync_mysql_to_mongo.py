import os
import pymysql
import time
from decimal import Decimal
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

# ⚡ Batch size for MongoDB bulk write (avoid connection closed errors)
BATCH_SIZE = 5000


# -----------------------------
# Convert Decimal → float and datetime → ISO
# -----------------------------
def convert_value(val):
    if isinstance(val, Decimal):
        return float(val)
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val


def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )


def sync_data():
    start_time = time.time()
    error_count = 0

    print("Connecting to MySQL...")
    conn = get_mysql_conn()

    print("Connecting to MongoDB...")
    mongo = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=60000,  # 60s timeout
        socketTimeoutMS=120000           # 2 min socket timeout
    )
    db = mongo[MONGO_DB]
    col = db["taxi_trips"]

    print("Fetching data from MySQL...")
    fetch_start = time.time()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM taxi_trips ORDER BY trip_id LIMIT 100000")
        rows = cur.fetchall()
    record_db_metrics("mysql", "sync_fetch", fetch_start, error_count=0)

    print(f"Syncing {len(rows)} records to MongoDB...")
    sync_start = time.time()

    # Convert all Decimal/datetime fields
    rows = [{k: convert_value(v) for k, v in r.items()} for r in rows]

    # Add timestamp
    for r in rows:
        r["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    # ⚡ Batch bulk writes
    total_synced = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        ops = [UpdateOne({"trip_id": r["trip_id"]}, {"$set": r}, upsert=True) for r in batch]

        try:
            result = col.bulk_write(ops, ordered=False)
            total_synced += len(batch)
            print(f"Synced batch {i//BATCH_SIZE + 1}: {len(batch)} documents (Inserted: {result.upserted_count}, Modified: {result.modified_count})")
        except Exception as e:
            error_count += 1
            print(f"Error during batch bulk write: {e}")

    record_db_metrics("mongodb", "sync_write", sync_start, error_count=error_count)
    record_db_metrics("mysql", "sync_complete", start_time, error_count=error_count)

    print(f"Sync completed successfully. Total documents synced: {total_synced}")

    conn.close()
    mongo.close()


if __name__ == "__main__":
    sync_data()
