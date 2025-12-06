import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_APP_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_APP_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB_NAME")

MIGRATIONS_DIR = "sql/migrations"

def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        autocommit=True
    )

def run_migrations():
    conn = get_conn()
    cursor = conn.cursor()

    # Get list of migration files
    import glob
    migration_files = sorted(glob.glob(f"{MIGRATIONS_DIR}/*.sql"))

    print(f"Found {len(migration_files)} migration files")

    for migration_file in migration_files:
        print(f"Running migration: {migration_file}")
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Split by semicolons and execute each statement
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        for statement in statements:
            try:
                cursor.execute(statement)
                print(f"  ✓ Executed statement")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                # Continue with next statement
                continue

    cursor.close()
    conn.close()
    print(" All migrations completed")

if __name__ == "__main__":
    run_migrations()