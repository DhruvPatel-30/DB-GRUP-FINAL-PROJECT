import os
import pymysql
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME"))

MONGO_URI = os.getenv("MONGODB_URI")

def get_mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def sync_data():
    conn = get_mysql_conn()
    mongo = MongoClient(MONGO_URI)
    db = mongo["taxi"]
    col = db["taxi_trips"]

    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute("SELECT * FROM taxi_trips")
        rows = cur.fetchall()

    ops = []
    for r in rows:
        ops.append(UpdateOne({"trip_id": r["trip_id"]}, {"$set": r}, upsert=True))

    if ops:
        col.bulk_write(ops)
        print(f"Synced {len(ops)} documents → MongoDB")

if __name__ == "__main__":
    sync_data()
