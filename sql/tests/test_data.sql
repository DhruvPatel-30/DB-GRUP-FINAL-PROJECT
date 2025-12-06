-- Test Data Verification
-- Verifies data was loaded correctly

USE nyc_taxi;

-- Test 1: Check if taxi_trips has data
SELECT 'Test 1: Checking taxi_trips has data...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN CONCAT('PASS: Found ', COUNT(*), ' records in taxi_trips')
        ELSE 'FAIL: No data in taxi_trips'
    END AS result
FROM taxi_trips;

-- Test 2: Check for NULL values in critical columns
SELECT 'Test 2: Checking for NULL values...' AS test;

SELECT 
    CONCAT('Null pickup_datetime: ', COUNT(*)) AS null_pickups,
    CONCAT('Null fare_amount: ', COUNT(CASE WHEN fare_amount IS NULL THEN 1 END)) AS null_fares,
    CONCAT('Null total_amount: ', COUNT(CASE WHEN total_amount IS NULL THEN 1 END)) AS null_totals
FROM taxi_trips;

-- Test 3: Check data ranges (detect bad data)
SELECT 'Test 3: Checking data quality...' AS test;

SELECT 
    CONCAT('Negative fares: ', COUNT(*)) AS result
FROM taxi_trips 
WHERE fare_amount < 0
UNION ALL
SELECT CONCAT('Zero distance trips: ', COUNT(*))
FROM taxi_trips 
WHERE trip_distance = 0
UNION ALL
SELECT CONCAT('Unrealistic fares (>$1000): ', COUNT(*))
FROM taxi_trips 
WHERE fare_amount > 1000;

-- Test 4: Check date ranges
SELECT 'Test 4: Checking date ranges...' AS test;

SELECT 
    CONCAT('Earliest trip: ', MIN(pickup_datetime)) AS earliest,
    CONCAT('Latest trip: ', MAX(pickup_datetime)) AS latest
FROM taxi_trips;

-- Test 5: Basic statistics
SELECT 'Test 5: Data statistics...' AS test;

SELECT 
    COUNT(*) AS total_records,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(trip_distance), 2) AS avg_distance,
    ROUND(AVG(total_amount), 2) AS avg_total
FROM taxi_trips;

-- Test 6: Check if anomalies were detected
SELECT 'Test 6: Checking anomaly detection...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN CONCAT('PASS: Found ', COUNT(*), ' anomalies')
        ELSE 'INFO: No anomalies detected yet (run anomaly_detection.py)'
    END AS result
FROM anomalies_taxi;

-- Summary
SELECT '===========================================' AS '';
SELECT 'DATA TEST SUMMARY' AS '';
SELECT '===========================================' AS '';