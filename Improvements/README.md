name: CI/CD - Multi DB NYC Taxi

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  ci-cd:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: ${{ secrets.MYSQL_ROOT_PASSWORD }}
          MYSQL_DATABASE: nyc_taxi
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping -h 127.0.0.1 -p$MYSQL_ROOT_PASSWORD"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    env:
      MYSQL_HOST: 127.0.0.1
      MYSQL_PORT: 3306
      MYSQL_DB_NAME: nyc_taxi
      MYSQL_ROOT_PASSWORD: ${{ secrets.MYSQL_ROOT_PASSWORD }}
      MYSQL_APP_USER: ${{ secrets.MYSQL_APP_USER }}
      MYSQL_APP_PASSWORD: ${{ secrets.MYSQL_APP_PASSWORD }}
      MONGODB_URI: ${{ secrets.MONGODB_URI }}
      MONGODB_DB_NAME: nyc_taxi_db
      DATASET_URL: ${{ secrets.DATASET_URL }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Wait for MySQL
        run: |
          echo "Waiting for MySQL..."
          for i in {1..30}; do
            if mysqladmin ping -h"$MYSQL_HOST" -P"$MYSQL_PORT" -uroot -p"$MYSQL_ROOT_PASSWORD" --silent; then
              echo "MySQL is up"
              break
            fi
            echo "Still waiting..."
            sleep 2
          done

      - name: Run MySQL migrations
        run: |
          python scripts/run_mysql_migrations.py

      - name: Setup MongoDB indexes
        run: |
          python mongo/setup_mongo.py

      - name: Run ETL to MySQL (NYC Taxi chunk load)
        run: |
          python scripts/etl_to_mysql.py

      - name: Sync MySQL to MongoDB
        run: |
          python scripts/sync_mysql_to_mongo.py

      - name: Run concurrent operations
        run: |
          python scripts/concurrent_ops.py

      - name: Validate MySQL ↔ MongoDB sync
        run: |
          python scripts/validate_sync.py

      - name: Run anomaly detection
        run: |
          python scripts/anomaly_detection.py

      - name: Upload Pipeline Logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-logs
          path: ./logs

      - name: Pipeline Complete
        run: |
          echo "CI/CD Pipeline completed successfully for commit $GITHUB_SHA"
          echo "All databases deployed, data loaded, synced, and validated."