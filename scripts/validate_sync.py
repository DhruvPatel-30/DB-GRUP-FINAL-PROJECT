import os
import pymysql
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DATABASE")

MONGO_URI = os.getenv("MONGO_URI")

def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB
    )

def main():
    conn = get_mysql_conn()
    mongo = MongoClient(MONGO_URI)
    col = mongo["taxi"]["taxi_trips"]

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT trip_id, fare_amount, total_amount FROM taxi_trips LIMIT 100")
        rows = cur.fetchall()

    mismatches = 0

    for r in rows:
        doc = col.find_one({"trip_id": r["trip_id"]})
        if not doc:
            mismatches += 1
        else:
            if float(doc["total_amount"]) != float(r["total_amount"]):
                mismatches += 1

    print("Validation complete.")
    print("Rows checked:", len(rows))
    print("Mismatches:", mismatches)

    if mismatches == 0:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
