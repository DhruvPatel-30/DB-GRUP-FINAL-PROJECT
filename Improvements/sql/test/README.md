# SQL Test Queries

This folder contains test queries to verify database setup and data integrity.

## Files

- `test_schema.sql` - Verify tables and schema are created correctly
- `test_data.sql` - Verify data was loaded successfully
- `test_performance.sql` - Test query performance
- `sample_queries.sql` - Example analytical queries

## How to Run Tests
```bash
# Run all tests
mysql -u root -p nyc_taxi < sql/test/test_schema.sql
mysql -u root -p nyc_taxi < sql/test/test_data.sql
mysql -u root -p nyc_taxi < sql/test/test_performance.sql
```

Or in Python:
```python
python scripts/run_tests.py
```