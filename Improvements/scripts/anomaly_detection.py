import os
import pymysql
import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import IsolationForest
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_APP_USER") or os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD") or os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB_NAME") or os.getenv("MYSQL_DATABASE", "nyc_taxi")

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGODB_DB_NAME", "nyc_taxi_db")

def mysql_conn():
    return pymysql.connect(
        host=MYSQL_HOST, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True
    )

def main():
    print("Starting anomaly detection...")
    conn = mysql_conn()

    # Fetch data from MySQL
    print("Fetching data from MySQL...")
    df = pd.read_sql("SELECT * FROM taxi_trips LIMIT 50000", conn)
    
    if len(df) == 0:
        print("⚠️  No data found in taxi_trips table. Skipping anomaly detection.")
        return

    print(f"Loaded {len(df)} records for analysis")

    # Prepare data for anomaly detection
    feature_cols = ["fare_amount", "trip_distance", "total_amount"]
    
    # Check if columns exist
    available_features = [col for col in feature_cols if col in df.columns]
    
    if len(available_features) == 0:
        print("⚠️  Required columns not found. Skipping anomaly detection.")
        return
    
    print(f"Using features: {available_features}")
    
    # Fill NaN values
    df_features = df[available_features].fillna(0)
    
    # Run Isolation Forest
    print("Running Isolation Forest model...")
    model = IsolationForest(contamination=0.01, random_state=42)
    df["anomaly"] = model.fit_predict(df_features)
    df["anomaly_score"] = model.score_samples(df_features)

    # Get anomalies
    anomalies = df[df["anomaly"] == -1].copy()
    print(f"Detected {len(anomalies)} anomalies ({len(anomalies)/len(df)*100:.2f}%)")

    if len(anomalies) == 0:
        print("No anomalies detected. Exiting.")
        return

    # Store in MongoDB
    print("Storing anomalies in MongoDB...")
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

    # Store in MySQL
    print("Storing anomalies in MySQL...")
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
            except Exception as e:
                print(f"Error inserting anomaly: {e}")
                continue

    print(f"✅ Stored {len(anomalies)} anomalies in MySQL")
    
    # Summary statistics
    print("\n" + "="*60)
    print("Anomaly Detection Summary:")
    print("="*60)
    print(f"Total records analyzed: {len(df)}")
    print(f"Anomalies detected:     {len(anomalies)}")
    print(f"Anomaly rate:           {len(anomalies)/len(df)*100:.2f}%")
    print(f"Avg anomaly score:      {anomalies['anomaly_score'].mean():.4f}")
    print("="*60)

    conn.close()
    mongo.close()

if __name__ == "__main__":
    main()