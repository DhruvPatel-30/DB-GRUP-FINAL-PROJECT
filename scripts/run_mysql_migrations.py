import os
import glob
import pymysql
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
PORT = int(os.getenv("MYSQL_PORT", "3306"))
DB_NAME = os.getenv("MYSQL_DB_NAME", "nyc_taxi")
ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD", "")
APP_USER = os.getenv("MYSQL_APP_USER", "app_user")
APP_PASSWORD = os.getenv("MYSQL_APP_PASSWORD", "app_password")

def run_sql(cursor, sql):
    for statement in sql.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)

def main():
    # Connect as root first to ensure DB and user exist
    root_conn = pymysql.connect(
        host=HOST,
        port=PORT,
        user="root",
        password=ROOT_PASSWORD,
        autocommit=True
    )
    with root_conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.execute(f"CREATE USER IF NOT EXISTS '{APP_USER}'@'%' IDENTIFIED BY '{APP_PASSWORD}'")
        cur.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{APP_USER}'@'%'")
        cur.execute("FLUSH PRIVILEGES")
    root_conn.close()

    # Connect as app user and run migrations
    conn = pymysql.connect(
        host=HOST,
        port=PORT,
        user=APP_USER,
        password=APP_PASSWORD,
        database=DB_NAME,
        autocommit=True
    )

    migration_files = sorted(glob.glob("sql/migrations/*.sql"))
    print("Running migrations:", migration_files)

    with conn.cursor() as cur:
        for path in migration_files:
            with open(path, "r", encoding="utf-8") as f:
                sql = f.read()
            print(f"Applying migration: {path}")
            run_sql(cur, sql)

    conn.close()
    print("All migrations applied successfully")

if __name__ == "__main__":
    main()
