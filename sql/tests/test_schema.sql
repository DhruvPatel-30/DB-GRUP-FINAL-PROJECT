-- Test Schema Verification
-- Verifies all tables exist and have correct structure

USE nyc_taxi;

-- Test 1: Check all required tables exist
SELECT 'Test 1: Checking tables exist...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) = 5 THEN 'PASS: All 5 tables exist'
        ELSE CONCAT('FAIL: Expected 5 tables, found ', COUNT(*))
    END AS result
FROM information_schema.tables 
WHERE table_schema = 'nyc_taxi'
AND table_name IN ('schema_version', 'taxi_trips', 'db_metrics', 'anomalies_taxi', 'etl_metrics');

-- Test 2: Check taxi_trips structure
SELECT 'Test 2: Checking taxi_trips columns...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) >= 19 THEN 'PASS: taxi_trips has required columns'
        ELSE CONCAT('FAIL: Expected 19+ columns, found ', COUNT(*))
    END AS result
FROM information_schema.columns 
WHERE table_schema = 'nyc_taxi' 
AND table_name = 'taxi_trips';

-- Test 3: Check indexes exist
SELECT 'Test 3: Checking indexes...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) >= 3 THEN 'PASS: Required indexes exist'
        ELSE CONCAT('FAIL: Expected 3+ indexes, found ', COUNT(*))
    END AS result
FROM information_schema.statistics 
WHERE table_schema = 'nyc_taxi' 
AND table_name = 'taxi_trips'
AND index_name != 'PRIMARY';

-- Test 4: Check anomalies_taxi table
SELECT 'Test 4: Checking anomalies_taxi table...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'PASS: anomalies_taxi table exists'
        ELSE 'FAIL: anomalies_taxi table not found'
    END AS result
FROM information_schema.tables 
WHERE table_schema = 'nyc_taxi' 
AND table_name = 'anomalies_taxi';

-- Test 5: Check db_metrics table
SELECT 'Test 5: Checking db_metrics table...' AS test;

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'PASS: db_metrics table exists'
        ELSE 'FAIL: db_metrics table not found'
    END AS result
FROM information_schema.tables 
WHERE table_schema = 'nyc_taxi' 
AND table_name = 'db_metrics';

-- Summary
SELECT '===========================================' AS '';
SELECT 'SCHEMA TEST SUMMARY' AS '';
SELECT '===========================================' AS '';