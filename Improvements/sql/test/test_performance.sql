-- Test Query Performance
-- Tests common query patterns and checks execution time

USE nyc_taxi;

-- Test 1: Simple SELECT performance
SELECT 'Test 1: Simple SELECT (should use PRIMARY KEY)' AS test;
SELECT * FROM taxi_trips WHERE trip_id = 1;

-- Test 2: Date range query (should use index)
SELECT 'Test 2: Date range query (should use idx_pickup_datetime)' AS test;
SELECT COUNT(*) 
FROM taxi_trips 
WHERE pickup_datetime BETWEEN '2023-01-01' AND '2023-01-31';

-- Test 3: Aggregation query
SELECT 'Test 3: Aggregation query' AS test;
SELECT 
    payment_type,
    COUNT(*) AS trip_count,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(trip_distance), 2) AS avg_distance
FROM taxi_trips
GROUP BY payment_type;

-- Test 4: Complex join (metrics)
SELECT 'Test 4: Join with metrics' AS test;
SELECT 
    DATE(t.pickup_datetime) AS trip_date,
    COUNT(t.trip_id) AS trips,
    SUM(t.total_amount) AS revenue
FROM taxi_trips t
WHERE t.pickup_datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(t.pickup_datetime)
ORDER BY trip_date DESC
LIMIT 10;

-- Test 5: Subquery performance
SELECT 'Test 5: Finding high-value trips' AS test;
SELECT trip_id, fare_amount, trip_distance, total_amount
FROM taxi_trips
WHERE total_amount > (SELECT AVG(total_amount) * 2 FROM taxi_trips)
LIMIT 10;

-- Show index usage
SELECT 'Index Usage Analysis' AS test;
EXPLAIN SELECT * FROM taxi_trips WHERE pickup_datetime > '2023-01-01' LIMIT 100;

-- Summary
SELECT '===========================================' AS '';
SELECT 'PERFORMANCE TEST COMPLETE' AS '';
SELECT '===========================================' AS '';