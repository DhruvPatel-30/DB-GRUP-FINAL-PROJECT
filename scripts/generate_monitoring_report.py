#!/usr/bin/env python3
"""
Generate a comprehensive monitoring report for the CI/CD pipeline.
"""
import os
import pymysql
from datetime import datetime
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
    print("GENERATING MONITORING REPORT")
    print("="*60)
    
    conn = get_conn()
    cursor = conn.cursor()
    
    os.makedirs("logs", exist_ok=True)
    report_path = "logs/monitoring_report.txt"
    
    with open(report_path, "w") as report:
        # Header
        report.write("="*70 + "\n")
        report.write("       NYC TAXI CI/CD PIPELINE - MONITORING REPORT\n")
        report.write("="*70 + "\n")
        report.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write("="*70 + "\n\n")
        
        # 1. Overall Metrics Summary
        cursor.execute("""
            SELECT 
                COUNT(*) as total_operations,
                COUNT(DISTINCT db_type) as databases_monitored,
                COUNT(DISTINCT operation) as operation_types,
                ROUND(AVG(cpu_percent), 2) as avg_cpu,
                ROUND(MAX(cpu_percent), 2) as max_cpu,
                ROUND(AVG(mem_percent), 2) as avg_mem,
                ROUND(MAX(mem_percent), 2) as max_mem,
                ROUND(AVG(avg_latency_ms), 2) as avg_latency,
                ROUND(MAX(avg_latency_ms), 2) as max_latency,
                SUM(error_count) as total_errors,
                SUM(mismatch_count) as total_mismatches
            FROM db_metrics
        """)
        
        summary = cursor.fetchone()
        
        report.write("1. OVERALL METRICS SUMMARY\n")
        report.write("-" * 70 + "\n")
        report.write(f"   Total Operations Monitored:    {summary['total_operations']}\n")
        report.write(f"   Databases:                     {summary['databases_monitored']}\n")
        report.write(f"   Operation Types:               {summary['operation_types']}\n")
        report.write(f"   Average CPU Usage:             {summary['avg_cpu']}%\n")
        report.write(f"   Peak CPU Usage:                {summary['max_cpu']}%\n")
        report.write(f"   Average Memory Usage:          {summary['avg_mem']}%\n")
        report.write(f"   Peak Memory Usage:             {summary['max_mem']}%\n")
        report.write(f"   Average Latency:               {summary['avg_latency']}ms\n")
        report.write(f"   Maximum Latency:               {summary['max_latency']}ms\n")
        report.write(f"   Total Errors:                  {summary['total_errors']}\n")
        report.write(f"   Total Mismatches:              {summary['total_mismatches']}\n")
        report.write("\n")
        
        # 2. Performance by Database Type
        cursor.execute("""
            SELECT 
                db_type,
                COUNT(*) as operations,
                ROUND(AVG(cpu_percent), 2) as avg_cpu,
                ROUND(AVG(mem_percent), 2) as avg_mem,
                ROUND(AVG(avg_latency_ms), 2) as avg_latency
            FROM db_metrics
            GROUP BY db_type
        """)
        
        report.write("2. PERFORMANCE BY DATABASE TYPE\n")
        report.write("-" * 70 + "\n")
        report.write(f"{'Database':<15} {'Operations':<15} {'Avg CPU%':<15} {'Avg Latency':<15}\n")
        report.write("-" * 70 + "\n")
        
        for row in cursor.fetchall():
            report.write(f"{row['db_type']:<15} {row['operations']:<15} "
                        f"{row['avg_cpu']:<15} {row['avg_latency']:<15}\n")
        report.write("\n")
        
        # 3. Top 5 Slowest Operations
        cursor.execute("""
            SELECT 
                operation,
                db_type,
                ROUND(avg_latency_ms, 2) as latency,
                ROUND(cpu_percent, 2) as cpu
            FROM db_metrics
            ORDER BY avg_latency_ms DESC
            LIMIT 5
        """)
        
        report.write("3. TOP 5 SLOWEST OPERATIONS\n")
        report.write("-" * 70 + "\n")
        report.write(f"{'Operation':<25} {'Database':<15} {'Latency (ms)':<15} {'CPU%':<10}\n")
        report.write("-" * 70 + "\n")
        
        for row in cursor.fetchall():
            report.write(f"{row['operation']:<25} {row['db_type']:<15} "
                        f"{row['latency']:<15} {row['cpu']:<10}\n")
        report.write("\n")
        
        # 4. Alert Threshold Analysis
        report.write("4. ALERT THRESHOLD ANALYSIS\n")
        report.write("-" * 70 + "\n")
        
        cursor.execute("SELECT COUNT(*) as count FROM db_metrics WHERE cpu_percent > 85")
        high_cpu = cursor.fetchone()['count']
        report.write(f"   High CPU Alerts (>85%):        {high_cpu}\n")
        
        cursor.execute("SELECT COUNT(*) as count FROM db_metrics WHERE avg_latency_ms > 500")
        slow_query = cursor.fetchone()['count']
        report.write(f"   Slow Query Alerts (>500ms):    {slow_query}\n")
        
        cursor.execute("SELECT SUM(mismatch_count) as total FROM db_metrics")
        mismatches = cursor.fetchone()['total'] or 0
        report.write(f"   Data Sync Mismatches:          {mismatches}\n")
        
        cursor.execute("SELECT SUM(error_count) as total FROM db_metrics")
        errors = cursor.fetchone()['total'] or 0
        report.write(f"   Errors Encountered:            {errors}\n")
        report.write("\n")
        
        # 5. Recommendations
        report.write("5. RECOMMENDATIONS\n")
        report.write("-" * 70 + "\n")
        
        if high_cpu > 0:
            report.write("   ⚠️  Consider optimizing high CPU operations\n")
        if slow_query > 0:
            report.write("   ⚠️  Review and optimize slow queries\n")
        if mismatches > 0:
            report.write("   ❌ Investigate data sync mismatches immediately\n")
        if errors > 0:
            report.write("   ⚠️  Review error logs and fix root causes\n")
        
        if high_cpu == 0 and slow_query == 0 and mismatches == 0 and errors == 0:
            report.write("   ✅ All metrics within acceptable thresholds\n")
            report.write("   ✅ Pipeline performance is optimal\n")
        
        report.write("\n")
        report.write("="*70 + "\n")
        report.write("                     END OF REPORT\n")
        report.write("="*70 + "\n")
    
    print(f"✅ Monitoring report generated: {report_path}")
    
    # Display key findings
    print("\n📊 KEY FINDINGS:")
    print(f"   - Total operations: {summary['total_operations']}")
    print(f"   - Average CPU: {summary['avg_cpu']}%")
    print(f"   - Average latency: {summary['avg_latency']}ms")
    print(f"   - Errors: {summary['total_errors']}")
    print(f"   - Mismatches: {summary['total_mismatches']}")
    
    conn.close()

if __name__ == "__main__":
    main()