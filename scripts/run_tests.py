import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

TEST_DIR = "sql/tests"

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def run_test_file(conn, filename):
    filepath = f"{TEST_DIR}/{filename}"
    
    if not os.path.exists(filepath):
        print(f"  Test file not found: {filepath}")
        return
    
    print(f"\n{'='*60}")
    print(f"Running: {filename}")
    print('='*60)
    
    with open(filepath, 'r') as f:
        sql = f.read()
    
    cursor = conn.cursor()
    
    # Split by semicolons and execute
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    for statement in statements:
        try:
            cursor.execute(statement)
            results = cursor.fetchall()
            
            for row in results:
                print(row[0] if len(row) == 1 else row)
        
        except Exception as e:
            print(f"Error: {e}")
    
    cursor.close()

def main():
    print(" Starting SQL Test Suite...")
    
    conn = get_conn()
    
    test_files = [
        "test_schema.sql",
        "test_data.sql",
        "test_performance.sql"
    ]
    
    for test_file in test_files:
        run_test_file(conn, test_file)
    
    conn.close()
    
    print("\n" + "="*60)
    print(" All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()