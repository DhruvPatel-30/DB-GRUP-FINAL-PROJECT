# 🚕 NYC Taxi Multi-Database CI/CD System

[![CI/CD Pipeline](https://github.com/DhruvPatel-30/DB-GRUP-FINAL-PROJECT/actions/workflows/ci_cd_pipeline.yml/badge.svg)](https://github.com/DhruvPatel-30/DB-GRUP-FINAL-PROJECT/actions)

> **PROG8850 Final Group Project** - Cross-Database Automation, Monitoring & Anomaly Detection with CI/CD

---

## 👥 Team Members

| Name | Role | Responsibilities |
|------|------|------------------|
| **Dhruv Patel** | DevOps Lead | Repository setup, CI/CD pipeline, ETL development |
| **Varun** | Database Engineer | MySQL/MongoDB schema, migrations, sync & validation |
| **Jay** | Performance Engineer | Concurrency testing, anomaly detection, monitoring |

---

## 📋 Project Overview

This project implements a **production-grade multi-database automation system** using the NYC Taxi Trip Records dataset. It integrates:

- ✅ **MySQL** (relational database) for transactional data
- ✅ **MongoDB** (document database) for flexible analytics
- ✅ **GitHub Actions** for automated CI/CD
- ✅ **Signoz + Grafana** for real-time monitoring
- ✅ **Machine Learning** for anomaly detection

### Key Features

- 🔄 Automated database deployment and schema evolution
- 📊 ETL pipeline processing 100,000+ taxi trip records
- 🔀 Real-time MySQL ↔ MongoDB synchronization
- ⚡ Concurrent operations testing (10 threads)
- 🤖 Isolation Forest ML model for anomaly detection
- 📈 Live monitoring dashboards with alerting
- ✅ Comprehensive data validation

---

## 🏗️ Architecture
```
┌─────────────────┐
│  GitHub Actions │  ← CI/CD Automation
└────────┬────────┘
         │
    ┌────▼────┐
    │  MySQL  │ ←→ Sync ←→ ┌──────────┐
    └────┬────┘              │ MongoDB  │
         │                   └─────┬────┘
         │                         │
    ┌────▼─────────────────────────▼────┐
    │     Monitoring (Signoz/Grafana)   │
    └───────────────────────────────────┘
              │
         ┌────▼──────┐
         │  Alerts   │
         └───────────┘
```

---

## 📁 Repository Structure
```
DB-GRUP-FINAL-PROJECT/
├── .github/workflows/
│   └── ci_cd_pipeline.yml          # Complete CI/CD automation
│
├── sql/
│   ├── migrations/                 # Flyway-style versioned migrations
│   │   ├── 001_create_schema_version.sql
│   │   ├── 002_create_taxi_trips.sql
│   │   ├── 003_create_metrics_and_anomalies.sql
│   │   └── 004_create_etl_metrics.sql
│   └── tests/                      # SQL test suite
│       ├── test_schema.sql
│       ├── test_data.sql
│       └── test_performance.sql
│
├── mongo/
│   └── setup_mongo.py              # MongoDB collection & index setup
│
├── scripts/
│   ├── etl_to_mysql.py             # Data extraction & loading
│   ├── sync_mysql_to_mongo.py      # Cross-database synchronization
│   ├── concurrent_ops.py           # Performance testing
│   ├── validate_sync.py            # Data consistency validation
│   ├── anomaly_detection.py        # ML anomaly detection
│   ├── monitoring_utils.py         # Metrics collection
│   ├── run_mysql_migrations.py     # Migration runner
│   └── run_tests.py                # Test suite runner
│
├── monitoring/
│   ├── docker-compose.yml          # Signoz + Grafana stack
│   ├── grafana/
│   │   ├── provisioning/           # Auto-configuration
│   │   └── dashboards/             # Dashboard JSON exports
│   └── signoz/
│       └── otel-collector-config.yaml
│
├── docs/
│   ├── optimization_recommendations.md
│   └── Final_Report_PROG8850.pdf
│
├── data/                           # Dataset cache (gitignored)
├── logs/                           # Application logs
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (gitignored)
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.0
- MongoDB 4.4+ (or MongoDB Atlas)
- Docker & Docker Compose (for monitoring)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/DhruvPatel-30/DB-GRUP-FINAL-PROJECT.git
cd DB-GRUP-FINAL-PROJECT
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required Environment Variables:**
```bash
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB_NAME=nyc_taxi
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_APP_USER=app_user
MYSQL_APP_PASSWORD=app_password

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017  # or your Atlas URI
MONGODB_DB_NAME=nyc_taxi_db

# Dataset
DATASET_URL=https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet
```

### 3. Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python scripts/run_mysql_migrations.py
python mongo/setup_mongo.py
```

### 5. Load Data (ETL Pipeline)
```bash
python scripts/etl_to_mysql.py
```

**Expected Output:**
```
Downloading dataset from URL...
Download complete.
Processing chunk 1...
Inserted 20000 rows. Total: 20000
Processing chunk 2...
Inserted 20000 rows. Total: 40000
...
ETL complete. Total rows: 100000 | Time: 45.23s
```

### 6. Sync to MongoDB
```bash
python scripts/sync_mysql_to_mongo.py
```

### 7. Run Tests & Validation
```bash
python scripts/validate_sync.py
python scripts/run_tests.py
```

### 8. Start Monitoring Stack
```bash
cd monitoring
docker-compose up -d
cd ..
```

**Access Dashboards:**
- Grafana: http://localhost:3000 (admin/admin)
- Signoz: http://localhost:3301

---

## 🔄 CI/CD Pipeline

The GitHub Actions pipeline automatically:

1. ✅ Sets up MySQL service container
2. ✅ Installs Python dependencies
3. ✅ Runs database migrations
4. ✅ Creates MongoDB indexes
5. ✅ Executes ETL pipeline (loads 100k records)
6. ✅ Syncs MySQL → MongoDB
7. ✅ Runs concurrent operations (10 threads)
8. ✅ Validates data consistency
9. ✅ Executes SQL test suite
10. ✅ Performs anomaly detection
11. ✅ Uploads logs as artifacts

**Triggered on:** Push to `main`, `dev`, or `feature/*` branches

**View Pipeline:** [GitHub Actions](https://github.com/DhruvPatel-30/DB-GRUP-FINAL-PROJECT/actions)

### GitHub Secrets Required:
```
MYSQL_ROOT_PASSWORD
MYSQL_APP_USER
MYSQL_APP_PASSWORD
MYSQL_DB_NAME
MONGODB_URI
DATASET_URL
```

---

## 📊 Database Schema

### MySQL Tables

#### `taxi_trips` - Main transactional data
- **19 columns**: `vendor_id`, `pickup_datetime`, `dropoff_datetime`, `fare_amount`, etc.
- **Indexes**: 
  - `idx_pickup_datetime` - Time-series queries
  - `idx_payment_pickup` - Payment analysis
  - `idx_fare_total` - Revenue calculations

#### `db_metrics` - Performance monitoring
- Tracks: CPU%, memory%, latency, errors, mismatches
- Used by: Grafana dashboards

#### `anomalies_taxi` - Detected anomalies
- Stores: trip_id, anomaly_type, score, details

#### `etl_metrics` - ETL performance
- Tracks: rows loaded, duration, timestamps

### MongoDB Collections

#### `taxi_trips` - Synced from MySQL
- Flexible JSON schema
- Indexes on: `pickup_datetime`, `payment_type`, `trip_id` (unique)

#### `anomalies_taxi` - Anomaly records
- Indexes on: `anomaly_type`, `trip_id`, `score`

---

## 🤖 Anomaly Detection

Uses **Isolation Forest** (scikit-learn) to detect outliers:

**Features:**
- `fare_amount` - Detects fare spikes
- `trip_distance` - Identifies unusual distances
- `total_amount` - Flags suspicious totals

**Configuration:**
- Contamination: 1% (assumes 1% anomaly rate)
- Detects ~500-1000 anomalies from 50,000 records

**Run Detection:**
```bash
python scripts/anomaly_detection.py
```

**Results stored in:**
- MySQL: `anomalies_taxi` table
- MongoDB: `anomalies_taxi` collection

---

## 📈 Monitoring & Alerting

### Grafana Dashboard: "NYC Taxi Database Monitoring"

**6 Panels:**
1. **CPU Usage** - By database type (MySQL/MongoDB)
2. **Memory Usage** - System memory consumption
3. **Query Latency** - Average response time by operation
4. **Sync Mismatches** - Data consistency errors
5. **Error Count** - Total errors in last hour
6. **Operations/Minute** - System throughput

### Alert Rules

| Alert | Condition | Action |
|-------|-----------|--------|
| High CPU | > 85% | Email notification |
| Slow Query | > 500ms | Email notification |
| Sync Mismatch | > 0 | Email notification |

**View Dashboards:**
- Grafana: http://localhost:3000
- Signoz Traces: http://localhost:3301

---

## ⚡ Performance Testing

### Concurrent Operations
```bash
python scripts/concurrent_ops.py
```

**Test Configuration:**
- 3 insert threads (300 inserts total)
- 2 update threads (batch updates)
- 5 select threads (aggregate queries)

**Typical Results:**
- Total duration: ~8-10 seconds
- No deadlocks
- Average latency: 450ms
- Error rate: 0%

---

## 🔧 Optimization Recommendations

Based on monitoring data:

### 1. Composite Index Optimization
```sql
CREATE INDEX idx_payment_pickup_fare 
ON taxi_trips (payment_type, pickup_datetime, fare_amount);
```
**Impact:** 70% latency reduction (650ms → 200ms)

### 2. Connection Pooling
```python
engine = create_engine(
    url, 
    pool_size=20, 
    max_overflow=30
)
```
**Impact:** Eliminate 2-3% connection errors

### 3. ETL Batch Size Tuning
```python
CHUNK_SIZE = 15000  # Reduced from 20000
```
**Impact:** Reduce memory usage from 82% → 65%

**Full details:** [docs/optimization_recommendations.md](docs/optimization_recommendations.md)

---

## 🧪 Testing

### Run All Tests
```bash
python scripts/run_tests.py
```

**Test Suites:**
1. **Schema Tests** - Verify table structure
2. **Data Tests** - Validate data quality
3. **Performance Tests** - Check query efficiency

### Manual Testing
```bash
# Test MySQL connection
mysql -h localhost -u app_user -p nyc_taxi

# Test MongoDB connection
mongosh "mongodb://localhost:27017/nyc_taxi_db"

# Verify data count
mysql -h localhost -u app_user -p nyc_taxi -e "SELECT COUNT(*) FROM taxi_trips;"
```

---

## 📚 Dataset

**Source:** NYC Taxi and Limousine Commission (TLC)

**Dataset Used:** Yellow Taxi Trip Records - January 2023

**Download:** https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet

**Size:** ~18 MB (3+ million records)

**Fields:** 19 columns including:
- Trip timestamps
- Pickup/dropoff locations
- Fare amounts
- Payment types
- Passenger counts

---

## 🛠️ Technologies Used

| Category | Tools |
|----------|-------|
| **Databases** | MySQL 8.0, MongoDB 4.4+ |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Grafana, Signoz, OpenTelemetry |
| **Programming** | Python 3.11 |
| **Libraries** | PyMySQL, PyMongo, Pandas, Scikit-learn, SQLAlchemy |
| **Containerization** | Docker, Docker Compose |
| **Data Format** | Parquet, JSON |

---

## 📝 Project Tasks Checklist

### ✅ Task 1: CI/CD Pipeline (20 pts)
- [x] GitHub repository with proper structure
- [x] GitHub Actions workflow
- [x] MySQL schema migrations
- [x] MongoDB setup scripts
- [x] ETL pipeline with chunking
- [x] Concurrent operations
- [x] Data validation
- [x] Comprehensive testing

### ✅ Task 2: Monitoring & Alerting (15 pts)
- [x] Signoz integration
- [x] Grafana dashboards (6 panels)
- [x] CPU, memory, latency monitoring
- [x] Alert configuration (>85% CPU, >500ms queries, mismatches)
- [x] Email/webhook notifications

### ✅ Task 3: Anomaly Detection & Optimization (10 pts)
- [x] Isolation Forest implementation
- [x] Anomaly storage in both databases
- [x] Performance analysis
- [x] 3-5 optimization recommendations

---

## 🚨 Troubleshooting

### MySQL Connection Issues
```bash
# Check MySQL is running
mysql -h localhost -u root -p -e "SELECT 1;"

# Grant permissions
mysql -u root -p <<EOF
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON nyc_taxi.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
EOF
```

### MongoDB Connection Issues
```bash
# Test connection
mongosh "mongodb://localhost:27017" --eval "db.adminCommand('ping')"

# Check indexes
mongosh "mongodb://localhost:27017/nyc_taxi_db" --eval "db.taxi_trips.getIndexes()"
```

### Docker Issues
```bash
# Restart all services
cd monitoring
docker-compose down -v
docker-compose up -d

# View logs
docker-compose logs -f grafana
docker-compose logs -f signoz-frontend
```

### Pipeline Failures
```bash
# Check logs
cat logs/alerts.log

# Verify data
mysql -h localhost -u app_user -p nyc_taxi -e "SELECT COUNT(*) FROM taxi_trips;"

# Re-run specific step
python scripts/etl_to_mysql.py
```

---

## 📖 Documentation

- **Project Report:** [docs/Final_Report_PROG8850.pdf](docs/Final_Report_PROG8850.pdf)
- **Optimization Guide:** [docs/optimization_recommendations.md](docs/optimization_recommendations.md)
- **API Docs:** Inline docstrings in Python files

---

## 🤝 Contributing

### Team Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -m "Add feature"`
3. Push to GitHub: `git push origin feature/your-feature`
4. Create Pull Request
5. Wait for CI/CD pipeline to pass
6. Merge to main

### Code Standards

- Python: PEP 8 style guide
- SQL: Uppercase keywords, snake_case identifiers
- Comments: Docstrings for all functions
- Commits: Descriptive messages

---

## 📄 License

This project is for educational purposes as part of PROG8850 - DevOps for Data Engineering.

**Course:** PROG8850  
**Institution:** Conestoga College  
**Semester:** Fall 2024

---

## 🎓 Learning Outcomes

Through this project, we learned:

1. ✅ **CI/CD Automation** - GitHub Actions for database pipelines
2. ✅ **Multi-Database Integration** - MySQL + MongoDB synchronization
3. ✅ **Real-Time Monitoring** - Grafana + Signoz implementation
4. ✅ **Machine Learning** - Anomaly detection with Isolation Forest
5. ✅ **Performance Optimization** - Index tuning, query optimization
6. ✅ **Concurrent Programming** - Thread-safe database operations
7. ✅ **DevOps Best Practices** - Version control, testing, monitoring

---

## 📞 Contact

**Dhruv Patel** - DevOps Lead  
**Varun** - Database Engineer  
**Jay** - Performance Engineer  

**GitHub:** [DhruvPatel-30/DB-GRUP-FINAL-PROJECT](https://github.com/DhruvPatel-30/DB-GRUP-FINAL-PROJECT)

---

## 🙏 Acknowledgments

- **Professor:** [Your Professor's Name]
- **Dataset:** NYC Taxi & Limousine Commission
- **Tools:** Grafana, Signoz, GitHub Actions
- **Inspiration:** Production-grade database automation systems

---

**⭐ If you found this project helpful, please star the repository!**

---

*Last Updated: December 2024*