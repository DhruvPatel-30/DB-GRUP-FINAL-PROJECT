import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "nyc_taxi_db")

def main():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]

    trips = db["taxi_trips"]
    anomalies = db["anomalies_taxi"]

    # Basic indexes
    trips.create_index([("pickup_datetime", ASCENDING)])
    trips.create_index([("payment_type", ASCENDING), ("pickup_datetime", ASCENDING)])
    anomalies.create_index([("anomaly_type", ASCENDING), ("created_at", ASCENDING)])

    print("Mongo indexes created successfully")

if __name__ == "__main__":
    main()
