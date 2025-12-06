-- Sample Analytical Queries
-- Useful queries for data analysis and reporting

USE nyc_taxi;

-- Query 1: Top 10 most profitable days
SELECT 
    DATE(pickup_datetime) AS trip_date,
    COUNT(*) AS total_trips,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS avg_fare
FROM taxi_trips
GROUP BY DATE(pickup_datetime)
ORDER BY total_revenue DESC
LIMIT 10;

-- Query 2: Payment type distribution
SELECT 
    payment_type,
    COUNT(*) AS trip_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM taxi_trips), 2) AS percentage
FROM taxi_trips
GROUP BY payment_type
ORDER BY trip_count DESC;

-- Query 3: Trip distance categories
SELECT 
    CASE 
        WHEN trip_distance <= 1 THEN '0-1 miles'
        WHEN trip_distance <= 3 THEN '1-3 miles'
        WHEN trip_distance <= 5 THEN '3-5 miles'
        WHEN trip_distance <= 10 THEN '5-10 miles'
        ELSE '10+ miles'
    END AS distance_category,
    COUNT(*) AS trip_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(total_amount), 2) AS avg_total
FROM taxi_trips
GROUP BY distance_category
ORDER BY trip_count DESC;

-- Query 4: Hourly trip patterns
SELECT 
    HOUR(pickup_datetime) AS hour_of_day,
    COUNT(*) AS trip_count,
    ROUND(AVG(total_amount), 2) AS avg_fare
FROM taxi_trips
GROUP BY HOUR(pickup_datetime)
ORDER BY hour_of_day;

-- Query 5: High tip percentage trips
SELECT 
    trip_id,
    fare_amount,
    tip_amount,
    ROUND((tip_amount / NULLIF(fare_amount, 0)) * 100, 2) AS tip_percentage
FROM taxi_trips
WHERE fare_amount > 0 
AND tip_amount > 0
ORDER BY tip_percentage DESC
LIMIT 20;

-- Query 6: Average metrics by vendor
SELECT 
    vendor_id,
    COUNT(*) AS trips,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(total_amount), 2) AS avg_total
FROM taxi_trips
GROUP BY vendor_id;

-- Query 7: Anomalies summary by type
SELECT 
    anomaly_type,
    COUNT(*) AS count,
    ROUND(AVG(score), 4) AS avg_score,
    MIN(created_at) AS first_detected,
    MAX(created_at) AS last_detected
FROM anomalies_taxi
GROUP BY anomaly_type;

-- Query 8: Join taxi trips with their anomalies
SELECT 
    t.trip_id,
    t.fare_amount,
    t.trip_distance,
    t.total_amount,
    a.anomaly_type,
    a.score
FROM taxi_trips t
INNER JOIN anomalies_taxi a ON t.trip_id = a.trip_id
ORDER BY a.score ASC
LIMIT 20;