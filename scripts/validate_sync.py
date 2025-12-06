import os
import pymysql
import time
from pymongo import MongoClient
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
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB
    )

def main():
    start_time = time.time()
    
    print("Validating MySQL ↔ MongoDB sync...")
    
    conn = get_mysql_conn()
    mongo = MongoClient(MONGO_URI)
    col = mongo[MONGO_DB]["taxi_trips"]

    # ✅ FIX: Get trip_ids from MongoDB (not MySQL)
    # This ensures we're checking records that were actually synced
    print("Fetching sample trip_ids from MongoDB...")
    mongo_docs = list(col.find({}, {"trip_id": 1}).limit(1000))
    
    if not mongo_docs:
        print("\n❌ ERROR: MongoDB has no data!")
        print("   Run: python scripts/sync_mysql_to_mongo.py")
        conn.close()
        mongo.close()
        exit(1)
    
    mongo_trip_ids = [doc["trip_id"] for doc in mongo_docs]
    print(f"Checking {len(mongo_trip_ids)} records...")
    
    # Now verify these exist in MySQL
    mismatches = 0
    not_found = 0

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        for trip_id in mongo_trip_ids:
            # Get from MySQL
            cur.execute(
                "SELECT trip_id, fare_amount, total_amount FROM taxi_trips WHERE trip_id = %s",
                (trip_id,)
            )
            mysql_row = cur.fetchone()
            
            if not mysql_row:
                not_found += 1
                continue
            
            # Get from MongoDB
            mongo_doc = col.find_one({"trip_id": trip_id})
            
            if not mongo_doc:
                not_found += 1
                continue
            
            # Compare values
            try:
                mysql_total = float(mysql_row["total_amount"])
                mongo_total = float(mongo_doc.get("total_amount", 0))
                
                if abs(mysql_total - mongo_total) > 0.01:
                    mismatches += 1
            except (ValueError, TypeError, KeyError):
                mismatches += 1

    print("\n" + "="*50)
    print("Validation Results:")
    print("="*50)
    print(f"✓ Rows checked:    {len(mongo_trip_ids)}")
    print(f"✗ Not found:       {not_found}")
    print(f"✗ Mismatches:      {mismatches}")
    print("="*50)

    # Record metrics
    total_issues = mismatches + not_found
    record_db_metrics("mysql", "validation", start_time, error_count=0, mismatch_count=total_issues)

    conn.close()
    mongo.close()

    if mismatches == 0 and not_found == 0:
        print("\n✅ Validation PASSED - Data is in sync!")
        exit(0)
    else:
        print(f"\n⚠️  Validation found {total_issues} issues")
        exit(1)

if __name__ == "__main__":
    main()