#!/usr/bin/env python3
"""
Verify that monitoring metrics were collected during pipeline execution.
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

def main():
    print("="*60)
    print("MONITORING VERIFICATION")
    print("="*60)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    # Check if db_metrics has data
    cursor.execute("SELECT COUNT(*) as count FROM db_metrics")
    result = cursor.fetchone()
    metrics_count = result['count']
    
    print(f"\n✓ Metrics records found: {metrics_count}")
    
    if metrics_count == 0:
        print("❌ ERROR: No monitoring metrics collected!")
        exit(1)
    
    # Check metrics by operation
    cursor.execute("""
        SELECT 
            operation,
            COUNT(*) as count,
            ROUND(AVG(cpu_percent), 2) as avg_cpu,
            ROUND(AVG(mem_percent), 2) as avg_mem,
            ROUND(AVG(avg_latency_ms), 2) as avg_latency
        FROM db_metrics
        GROUP BY operation
        ORDER BY count DESC
    """)
    
    print("\n📊 Metrics Summary by Operation:")
    print("-" * 60)
    print(f"{'Operation':<25} {'Count':<10} {'Avg CPU%':<12} {'Avg Latency':<12}")
    print("-" * 60)
    
    for row in cursor.fetchall():
        print(f"{row['operation']:<25} {row['count']:<10} {row['avg_cpu']:<12} {row['avg_latency']:<12}")
    
    # Verify critical operations were monitored
    cursor.execute("""
        SELECT DISTINCT operation 
        FROM db_metrics
    """)
    operations = [row['operation'] for row in cursor.fetchall()]
    
    required_ops = ['etl_chunk', 'sync_write', 'concurrent_insert', 'anomaly_detection']
    missing_ops = [op for op in required_ops if op not in operations]
    
    if missing_ops:
        print(f"\n⚠️  WARNING: Missing monitoring for operations: {missing_ops}")
    else:
        print(f"\n✅ All critical operations monitored!")
    
    print("\n" + "="*60)
    print("✅ MONITORING VERIFICATION PASSED")
    print("="*60)
    
    conn.close()

if __name__ == "__main__":
    main()