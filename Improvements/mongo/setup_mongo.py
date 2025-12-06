import os
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "nyc_taxi_db")

def main():
    print("Connecting to MongoDB...")
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]

    print("Setting up collections and indexes...")
    
    trips = db["taxi_trips"]
    anomalies = db["anomalies_taxi"]

    # Create indexes for taxi_trips
    print("Creating indexes on taxi_trips...")
    trips.create_index([("pickup_datetime", ASCENDING)])
    trips.create_index([("payment_type", ASCENDING), ("pickup_datetime", ASCENDING)])
    trips.create_index([("trip_id", ASCENDING)], unique=True)
    
    # Create indexes for anomalies
    print("Creating indexes on anomalies_taxi...")
    anomalies.create_index([("anomaly_type", ASCENDING), ("created_at", ASCENDING)])
    anomalies.create_index([("trip_id", ASCENDING)])
    anomalies.create_index([("score", ASCENDING)])

    print("✅ MongoDB indexes created successfully")
    
    # Print collection stats
    print(f"\nCollection stats:")
    print(f"  taxi_trips: {trips.count_documents({})} documents")
    print(f"  anomalies_taxi: {anomalies.count_documents({})} documents")
    
    client.close()

if __name__ == "__main__":
    main()
```

## 9. **Updated Requirements**

**File: `requirements.txt`**
```
pymysql
pymongo
python-dotenv
pandas
numpy
scikit-learn
psutil
sqlalchemy
opentelemetry-sdk
opentelemetry-exporter-otlp
opentelemetry-instrumentation
pyarrow
fastparquet
requests
```

## 10. **Create .gitignore**

**File: `.gitignore`**
```
# Environment
.env
*.env

# Data files
data/*.csv
data/*.parquet
data/*.json

# Logs
logs/*.log
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db