CREATE TABLE IF NOT EXISTS db_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    db_type VARCHAR(10) NOT NULL,           -- 'mysql' or 'mongo'
    operation VARCHAR(50) NOT NULL,         -- 'etl', 'concurrent_ops', 'anomaly_detection'
    cpu_percent DOUBLE,
    mem_percent DOUBLE,
    avg_latency_ms DOUBLE,
    error_count INT,
    mismatch_count INT
);

CREATE TABLE IF NOT EXISTS anomalies_taxi (
    anomaly_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    trip_id BIGINT,
    source_db VARCHAR(10) NOT NULL,         -- 'mysql' or 'mongo'
    anomaly_type VARCHAR(50) NOT NULL,      -- 'fare_spike', 'distance_spike', 'missing_values', etc.
    score DOUBLE,
    details JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
