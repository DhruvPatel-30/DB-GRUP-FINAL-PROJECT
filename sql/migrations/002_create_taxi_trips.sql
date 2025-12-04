CREATE TABLE IF NOT EXISTS taxi_trips (
    trip_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    vendor_id VARCHAR(10),
    pickup_datetime DATETIME,
    dropoff_datetime DATETIME,
    passenger_count INT,
    trip_distance DOUBLE,
    rate_code_id INT,
    store_and_fwd_flag CHAR(1),
    pu_location_id INT,
    do_location_id INT,
    payment_type INT,
    fare_amount DECIMAL(10,2),
    extra DECIMAL(10,2),
    mta_tax DECIMAL(10,2),
    tip_amount DECIMAL(10,2),
    tolls_amount DECIMAL(10,2),
    improvement_surcharge DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    congestion_surcharge DECIMAL(10,2),
    airport_fee DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Helpful indexes for analytics and performance monitoring
CREATE INDEX idx_pickup_datetime ON taxi_trips (pickup_datetime);
CREATE INDEX idx_payment_pickup ON taxi_trips (payment_type, pickup_datetime);
CREATE INDEX idx_fare_total ON taxi_trips (fare_amount, total_amount);
