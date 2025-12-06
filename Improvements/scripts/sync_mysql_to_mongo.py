import os
import pymysql
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_APP_USER") or os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB_NAME") or os.getenv("MYSQL_DATABASE", "nyc_taxi")

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
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
    print("Connecting to MySQL...")
    conn = get_mysql_conn()
    
    print("Connecting to MongoDB...")
    mongo = MongoClient(MONGO_URI)
    db = mongo[MONGO_DB]
    col = db["taxi_trips"]

    print("Fetching data from MySQL...")
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM taxi_trips LIMIT 100000")  # Limit for performance
        rows = cur.fetchall()

    print(f"Syncing {len(rows)} records to MongoDB...")
    ops = []
    for r in rows:
        # Convert datetime objects to strings for MongoDB
        for key, val in r.items():
            if hasattr(val, 'isoformat'):
                r[key] = val.isoformat()
        
        ops.append(UpdateOne({"trip_id": r["trip_id"]}, {"$set": r}, upsert=True))

    if ops:
        result = col.bulk_write(ops)
        print(f"✅ Synced {len(ops)} documents → MongoDB")
        print(f"   Inserted: {result.upserted_count}, Modified: {result.modified_count}")
    else:
        print("No data to sync")
    
    conn.close()
    mongo.close()

if __name__ == "__main__":
    sync_data()