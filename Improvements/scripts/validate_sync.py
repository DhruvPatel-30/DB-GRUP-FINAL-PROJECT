import os
import pymysql
from pymongo import MongoClient
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
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB
    )

def main():
    print("Validating MySQL ↔ MongoDB sync...")
    
    conn = get_mysql_conn()
    mongo = MongoClient(MONGO_URI)
    col = mongo[MONGO_DB]["taxi_trips"]

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT trip_id, fare_amount, total_amount FROM taxi_trips LIMIT 1000")
        rows = cur.fetchall()

    print(f"Checking {len(rows)} records...")
    mismatches = 0
    not_found = 0

    for r in rows:
        doc = col.find_one({"trip_id": r["trip_id"]})
        if not doc:
            not_found += 1
        else:
            # Compare key fields
            try:
                if abs(float(doc.get("total_amount", 0)) - float(r["total_amount"])) > 0.01:
                    mismatches += 1
            except (ValueError, TypeError):
                mismatches += 1

    print("\n" + "="*50)
    print("Validation Results:")
    print("="*50)
    print(f"✓ Rows checked:    {len(rows)}")
    print(f"✗ Not found:       {not_found}")
    print(f"✗ Mismatches:      {mismatches}")
    print("="*50)

    conn.close()
    mongo.close()

    if mismatches == 0 and not_found == 0:
        print("\n Validation PASSED - Data is in sync!")
        exit(0)
    else:
        print(f"\n  Validation found {mismatches + not_found} issues")
        exit(1)

if __name__ == "__main__":
    main()