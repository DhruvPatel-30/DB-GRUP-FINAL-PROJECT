import os
import pymysql
import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

MONGO_URI = os.getenv("MONGODB_URI")

def mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True
    )

def main():
    conn = mysql_conn()

    df = pd.read_sql("SELECT * FROM taxi_trips LIMIT 50000", conn)

    model = IsolationForest(contamination=0.01)
    df["anomaly"] = model.fit_predict(df[["fare_amount", "trip_distance", "total_amount"]])

    anomalies = df[df["anomaly"] == -1]

    mongo = MongoClient(MONGO_URI)
    col = mongo["taxi"]["anomalies"]
    col.insert_many(anomalies.to_dict("records"))

    with conn.cursor() as cur:
        for _, row in anomalies.iterrows():
            cur.execute("""
                INSERT INTO anomalies (trip_id, fare_amount, total_amount, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (row["trip_id"], row["fare_amount"], row["total_amount"]))

    print(f"Stored {len(anomalies)} anomalies (MySQL + MongoDB).")

if __name__ == "__main__":
    main()
