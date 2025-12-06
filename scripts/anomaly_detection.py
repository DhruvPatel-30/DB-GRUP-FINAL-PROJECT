import os
import pymysql
import pandas as pd
import time
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
from datetime import datetime
from dotenv import load_dotenv
from monitoring_utils import record_db_metrics

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB = os.getenv("MONGODB_DB_NAME", "nyc_taxi_db")

def mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True
    )

def main():
    overall_start = time.time()
    error_count = 0
    
    print("="*60)
    print("🔍 Starting Anomaly Detection...")
    print("="*60)
    
    conn = mysql_conn()

    # Fetch data
    fetch_start = time.time()
    print("📊 Fetching data from MySQL...")
    df = pd.read_sql("SELECT * FROM taxi_trips LIMIT 50000", conn)
    record_db_metrics("mysql", "anomaly_fetch", fetch_start, error_count=0)
    
    if len(df) == 0:
        print("⚠️  No data found in taxi_trips table. Skipping anomaly detection.")
        return

    print(f"✅ Loaded {len(df)} records for analysis")

    # Prepare features
    feature_cols = ["fare_amount", "trip_distance", "total_amount"]
    available_features = [col for col in feature_cols if col in df.columns]
    
    if len(available_features) == 0:
        print("⚠️  Required columns not found. Skipping anomaly detection.")
        return
    
    print(f"📈 Using features: {available_features}")
    df_features = df[available_features].fillna(0)
    
    # Run model
    model_start = time.time()
    print("🤖 Running Isolation Forest model...")
    model = IsolationForest(contamination=0.01, random_state=42)
    df["anomaly"] = model.fit_predict(df_features)
    df["anomaly_score"] = model.score_samples(df_features)
    record_db_metrics("mysql", "anomaly_model", model_start, error_count=0)

    anomalies = df[df["anomaly"] == -1].copy()
    print(f"🎯 Detected {len(anomalies)} anomalies ({len(anomalies)/len(df)*100:.2f}%)")

    if len(anomalies) == 0:
        print("✅ No anomalies detected. Exiting.")
        record_db_metrics("mysql", "anomaly_complete", overall_start, error_count=0)
        return

    # Store in MongoDB
    store_start = time.time()
    print("💾 Storing anomalies in MongoDB...")
    try:
        mongo = MongoClient(MONGO_URI)
        col = mongo[MONGO_DB]["anomalies_taxi"]
        
        anomalies_dict = []
        for _, row in anomalies.iterrows():
            record = {
                "trip_id": int(row.get("trip_id", 0)),
                "source_db": "mysql",
                "anomaly_type": "isolation_forest",
                "score": float(row["anomaly_score"]),
                "details": {
                    "fare_amount": float(row.get("fare_amount", 0)),
                    "trip_distance": float(row.get("trip_distance", 0)),
                    "total_amount": float(row.get("total_amount", 0))
                },
                "created_at": datetime.now()
            }
            anomalies_dict.append(record)
        
        if anomalies_dict:
            col.insert_many(anomalies_dict)
            print(f"✅ Stored {len(anomalies_dict)} anomalies in MongoDB")
        
        mongo.close()
    except Exception as e:
        error_count += 1
        print(f"❌ Error storing in MongoDB: {e}")
    
    record_db_metrics("mongodb", "anomaly_store", store_start, error_count=error_count)

    # Store in MySQL
    print("💾 Storing anomalies in MySQL...")
    mysql_store_start = time.time()
    stored_count = 0
    
    with conn.cursor() as cur:
        for _, row in anomalies.iterrows():
            try:
                cur.execute("""
                    INSERT INTO anomalies_taxi (trip_id, source_db, anomaly_type, score, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (
                    int(row.get("trip_id", 0)),
                    "mysql",
                    "isolation_forest",
                    float(row["anomaly_score"])
                ))
                stored_count += 1
            except Exception as e:
                error_count += 1
                continue

    print(f"✅ Stored {stored_count} anomalies in MySQL")
    record_db_metrics("mysql", "anomaly_store", mysql_store_start, error_count=error_count)
    
    # Summary
    duration = time.time() - overall_start
    print("\n" + "="*60)
    print("📊 Anomaly Detection Summary:")
    print("="*60)
    print(f"Total Records Analyzed:  {len(df)}")
    print(f"Anomalies Detected:      {len(anomalies)} ({len(anomalies)/len(df)*100:.2f}%)")
    print(f"Stored in MySQL:         {stored_count}")
    print(f"Stored in MongoDB:       {len(anomalies_dict) if anomalies_dict else 0}")
    print(f"Total Duration:          {duration:.2f}s")
    print(f"Errors Encountered:      {error_count}")
    print("="*60)
    
    record_db_metrics("mysql", "anomaly_complete", overall_start, error_count=error_count)
    conn.close()

if __name__ == "__main__":
    main()