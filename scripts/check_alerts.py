#!/usr/bin/env python3
"""
Check if any alert thresholds were exceeded during pipeline execution.
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
    print("ALERT THRESHOLD CHECK")
    print("="*60)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    alerts_triggered = []
    
    # Check 1: High CPU (>85%)
    cursor.execute("""
        SELECT COUNT(*) as count, MAX(cpu_percent) as max_cpu
        FROM db_metrics
        WHERE cpu_percent > 85
    """)
    result = cursor.fetchone()
    if result['count'] > 0:
        alerts_triggered.append(f"🚨 HIGH CPU: {result['count']} instances, Max: {result['max_cpu']:.1f}%")
    else:
        print("✅ CPU usage within normal range (<85%)")
    
    # Check 2: Slow queries (>500ms)
    cursor.execute("""
        SELECT COUNT(*) as count, MAX(avg_latency_ms) as max_latency
        FROM db_metrics
        WHERE avg_latency_ms > 500
    """)
    result = cursor.fetchone()
    if result['count'] > 0:
        alerts_triggered.append(f"⚠️  SLOW QUERIES: {result['count']} instances, Max: {result['max_latency']:.1f}ms")
    else:
        print("✅ Query latency within acceptable range (<500ms)")
    
    # Check 3: Data mismatches
    cursor.execute("""
        SELECT SUM(mismatch_count) as total_mismatches
        FROM db_metrics
        WHERE mismatch_count > 0
    """)
    result = cursor.fetchone()
    if result['total_mismatches'] and result['total_mismatches'] > 0:
        alerts_triggered.append(f"❌ DATA MISMATCHES: {result['total_mismatches']} total mismatches found")
    else:
        print("✅ No data sync mismatches detected")
    
    # Check 4: Errors
    cursor.execute("""
        SELECT SUM(error_count) as total_errors
        FROM db_metrics
        WHERE error_count > 0
    """)
    result = cursor.fetchone()
    if result['total_errors'] and result['total_errors'] > 0:
        alerts_triggered.append(f"⚠️  ERRORS: {result['total_errors']} errors encountered")
    else:
        print("✅ No errors detected")
    
    # Summary
    print("\n" + "="*60)
    if alerts_triggered:
        print("⚠️  ALERTS TRIGGERED:")
        print("="*60)
        for alert in alerts_triggered:
            print(alert)
        print("\n💡 These alerts would trigger notifications in production")
    else:
        print("✅ NO ALERTS TRIGGERED - All metrics within thresholds")
    print("="*60)
    
    # Write to alert log
    os.makedirs("logs", exist_ok=True)
    with open("logs/alerts.log", "a") as f:
        f.write("\n" + "="*60 + "\n")
        f.write(f"CI/CD Pipeline Alert Check\n")
        f.write("="*60 + "\n")
        if alerts_triggered:
            for alert in alerts_triggered:
                f.write(f"{alert}\n")
        else:
            f.write("No alerts triggered - all metrics within normal range\n")
    
    conn.close()

if __name__ == "__main__":
    main()