👤 Dhruv Patel – Member 1 (you)
Section 1: Repository Setup + Project Structure
Describe creating the GitHub repository

Adding core folders (sql/, mongo/, scripts/, workflows/)

Writing or organizing requirements.txt, README, and initial migrations

Setting up Codespaces to run scripts

Adding and organizing chunked ETL + Python scripts you updated

Section 2: ETL + Data Pipeline Explanation
Write how you handled:

etl_to_mysql.py (chunking, cleaning, inserting)

Any troubleshooting (e.g., cryptography error)

Coordinating file structure with the group

Making sure GitHub Actions runs scripts correctly

Section 3: CI/CD Verification
Describe how you tested or prepared pipeline steps

Screenshots of:

GitHub Actions passing

Folder structure

Successful script runs or dry-run




👤 Member 2 – (V K / user-NNGDirTcJjfEIK7XHmqMiwcx)
Section 1: MySQL + MongoDB Schema Work
Explain migration scripts:

001_create_schema_version.sql

002_create_taxi_trips.sql

003_create_metrics_and_anomalies.sql

Purpose of each table

Why indexes were added (performance, latency monitoring)

Section 2: MongoDB Setup
Document setup_mongo.py

Database creation, index creation, connection

Why MongoDB is useful for analytics + JSON flexibility

Section 3: Sync + Validation
Explain scripts the member helped with:

sync_mysql_to_mongo.py

validate_sync.py

Include screenshots of:

MongoDB collections

Validation output

Database comparing results





👤 Member 3 – (jay)
Section 1: Concurrency + Performance Testing
Document:

concurrent_ops.py — multithreaded inserts + queries

Why concurrency matters in real systems

Metrics generated (latency, errors, time per batch)

Section 2: Anomaly Detection Module
Explain:

anomaly_detection.py (outlier fares, distance spikes, missing values, etc.)

What statistical model was chosen (IQR, Z‑Score, Isolation Forest, etc.)

How anomalies are stored in MySQL/MongoDB

Include screenshots of:

Output logs

Anomalies table or collection

Section 3: Optimization Recommendations
3–5 performance suggestions based on:

Signoz/Grafana metrics

Index improvements

Query rewrites

ETL batching







📊 Shared Group Sections (everyone writes 1–2 sentences each)
Every member should contribute a little to these sections so Track Changes shows participation:

Introduction
What the project is

Tools used (MySQL, MongoDB, Actions, Grafana, Signoz, Python, ETL, concurrency)

Monitoring + Alerting Section
Include screenshots:

Grafana dashboards

Signoz traces

Alerts triggered (CPU, slow queries, sync mismatches)

Everyone can contribute 1 screenshot + explanation.

Conclusion
Each member adds:

What they learned

Improvements for real production setup


.
.