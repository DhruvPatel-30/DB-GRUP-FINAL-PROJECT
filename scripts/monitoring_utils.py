import psutil
import time
from datetime import datetime
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

def get_conn():
    try:
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            autocommit=True
        )
    except Exception as e:
        print(f"  Failed to connect to MySQL: {e}")
        return None

def record_db_metrics(db_type, operation, start_time, error_count=0, mismatch_count=0):
    """Record performance metrics to db_metrics table"""
    try:
        conn = get_conn()
        if not conn:
            return
        
        # Get system metrics
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        duration_ms = (time.time() - start_time) * 1000
        
        sql = """
            INSERT INTO db_metrics 
            (db_type, operation, cpu_percent, mem_percent, avg_latency_ms, error_count, mismatch_count, recorded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        with conn.cursor() as cur:
            cur.execute(sql, (db_type, operation, cpu, mem, duration_ms, error_count, mismatch_count))
        
        print(f"📊 Metrics: {db_type}.{operation} | CPU: {cpu:.1f}% | Mem: {mem:.1f}% | Latency: {duration_ms:.2f}ms")
        
        # Check for alerts
        check_alerts(cpu, duration_ms, mismatch_count)
        
        conn.close()
        
    except Exception as e:
        print(f"  Failed to record metrics: {e}")

def check_alerts(cpu, latency_ms, mismatches):
    """Check alert thresholds and log warnings"""
    alerts = []
    
    if cpu > 85:
        alerts.append(f"🚨 HIGH CPU ALERT: {cpu:.1f}% (threshold: 85%)")
    
    if latency_ms > 500:
        alerts.append(f"⚠️  SLOW QUERY ALERT: {latency_ms:.2f}ms (threshold: 500ms)")
    
    if mismatches > 0:
        alerts.append(f"❌ DATA MISMATCH ALERT: {mismatches} mismatches found")
    
    for alert in alerts:
        print(alert)
        log_alert(alert)

def log_alert(message):
    """Log alert to file"""
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/alerts.log", "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"Failed to log alert: {e}")

def get_metrics_summary():
    """Get recent metrics summary"""
    conn = get_conn()
    if not conn:
        return []
    
    sql = """
        SELECT 
            db_type,
            operation,
            COUNT(*) as count,
            ROUND(AVG(cpu_percent), 2) as avg_cpu,
            ROUND(AVG(mem_percent), 2) as avg_mem,
            ROUND(AVG(avg_latency_ms), 2) as avg_latency,
            ROUND(MAX(avg_latency_ms), 2) as max_latency,
            SUM(error_count) as total_errors,
            SUM(mismatch_count) as total_mismatches
        FROM db_metrics
        WHERE recorded_at > NOW() - INTERVAL 1 HOUR
        GROUP BY db_type, operation
        ORDER BY avg_latency DESC
    """
    
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql)
            results = cur.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Failed to get metrics summary: {e}")
        return []

def print_metrics_summary():
    """Print formatted metrics summary"""
    print("\n" + "="*90)
    print("📊 PERFORMANCE METRICS SUMMARY (Last Hour)")
    print("="*90)
    
    metrics = get_metrics_summary()
    
    if not metrics:
        print("No metrics available yet.")
        return
    
    print(f"{'Database':<10} {'Operation':<20} {'Count':<8} {'Avg CPU':<10} {'Avg Latency':<15} {'Errors':<8}")
    print("-"*90)
    
    for m in metrics:
        print(f"{m['db_type']:<10} {m['operation']:<20} {m['count']:<8} "
              f"{m['avg_cpu']:.1f}%{'':<6} {m['avg_latency']:.1f}ms{'':<9} "
              f"{m['total_errors']:<8}")
    
    print("="*90 + "\n")

if __name__ == "__main__":
    # Test metrics collection
    print("Testing metrics collection...")
    
    start = time.time()
    time.sleep(1)  # Simulate work
    
    record_db_metrics("mysql", "test", start, error_count=0, mismatch_count=0)
    
    print("\nMetrics Summary:")
    print_metrics_summary()