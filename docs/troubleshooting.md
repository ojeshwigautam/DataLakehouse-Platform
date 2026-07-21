# Troubleshooting Guide

Common issues encountered while setting up and running the Unified Commerce Lakehouse platform, along with their solutions.

---

## Table of Contents

- [Java & Spark Issues](#java--spark-issues)
- [Docker Issues](#docker-issues)
- [PostgreSQL Issues](#postgresql-issues)
- [Airflow Issues](#airflow-issues)
- [Python & Dependency Issues](#python--dependency-issues)
- [Validation Issues](#validation-issues)
- [Permission Issues](#permission-issues)

---

## Java & Spark Issues

### `Java gateway process exited before sending its port number`

**Cause:** Java is not installed or `JAVA_HOME` is not set.

**Solution:**

```bash
# Check Java installation
java -version

# Set JAVA_HOME (Windows)
set JAVA_HOME=C:\Program Files\Java\jdk-17

# Set JAVA_HOME (macOS/Linux)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

### `PySpark requires Java 17+`

**Cause:** The project uses PySpark 4.0.0 which requires Java 17 or later.

**Solution:** Install Java 17 (Temurin recommended):
```bash
# Download from https://adoptium.net/
# Verify version
java -version  # Should show "openjdk version 17.x.x"
```

### SparkSession fails to create

**Cause:** Missing or incompatible PySpark version.

**Solution:**
```bash
# Verify PySpark installation
python -c "import pyspark; print(pyspark.__version__)"

# If missing, install from requirements
pip install -r requirements.txt
```

### Spark UI not accessible

**Cause:** Spark is running in local mode (`local[*]`). The Spark UI only binds to `localhost:4040` by default.

**Solution:** Access the Spark UI at `http://localhost:4040` while a Spark application is running. If running in Docker, ensure port mapping is configured.

---

## Docker Issues

### Port conflict on 5432

**Cause:** A local PostgreSQL instance is already running on port 5432.

**Solution:** The Docker Compose maps PostgreSQL to port **5433** by default to avoid conflicts. Use:
```bash
# Connect to PostgreSQL via mapped port
psql -h localhost -p 5433 -U postgres -d commerce_lakehouse
```

### Docker Compose exits immediately

**Cause:** The ETL container runs the pipeline once and exits.

**Solution:** This is expected behavior. Check logs for success/failure:
```bash
# Check if pipeline completed successfully
docker logs commerce_lakehouse_etl --tail 50

# Verify all services
docker-compose ps
```

### `docker: command not found`

**Cause:** Docker is not installed or not in PATH.

**Solution:**
- Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
- Ensure Docker is running (check system tray)

### Docker build fails with `no matching manifest for windows/amd64`

**Cause:** Cross-platform image incompatibility on Windows.

**Solution:** Ensure Docker Desktop is configured to use Linux containers. Switch from Windows to Linux containers in Docker Desktop settings.

### `ERROR: Service 'spark' failed to build`

**Cause:** The Spark image `apache/spark:4.2.0` may not be available on your architecture.

**Solution:**
```bash
# Try pulling the image first
docker pull apache/spark:4.2.0

# Check available tags at https://hub.docker.com/r/apache/spark
```

---

## PostgreSQL Issues

### `Connection refused` to PostgreSQL

**Cause:** PostgreSQL is not running or not reachable.

**Solution:**

```bash
# If using Docker
docker-compose up -d postgres
docker-compose ps postgres

# Check if PostgreSQL is healthy
docker inspect --format='{{json .State.Health}}' commerce_lakehouse_postgres

# Test connection
python -c "
from src.database.connection import get_database_engine
engine = get_database_engine()
print('Connected successfully')
"
```

### `FATAL: password authentication failed for user "postgres"`

**Cause:** Password mismatch or incorrect environment variables.

**Solution:**
```bash
# Verify environment variables are set correctly
echo DB_HOST=$DB_HOST DB_PORT=$DB_PORT DB_NAME=$DB_NAME DB_USER=$DB_USER

# Default credentials for Docker:
# Host: localhost / Port: 5433 / User: postgres / Password: postgres / DB: commerce_lakehouse
```

### `relation "daily_sales" does not exist`

**Cause:** Gold tables have not been loaded into PostgreSQL yet.

**Solution:** Run the full pipeline or load tables directly:
```bash
python main.py
# Or
python -m src.database.load_gold_tables
```

### `schema "metadata" does not exist`

**Cause:** The metadata schema has not been initialized.

**Solution:** Run the MetadataManager to create schema and tables:
```bash
python -c "
from src.metadata.metadata_manager import MetadataManager
mgr = MetadataManager()
mgr.create_tables()
"
```

---

## Airflow Issues

### Airflow scheduler or webserver won't start

**Cause:** Port conflicts or dependency issues.

**Solution:**

```bash
# Check Airflow container logs
docker logs commerce_airflow_scheduler
docker logs commerce_airflow_webserver

# Verify port 8081 is not in use
netstat -ano | findstr :8081  # Windows
lsof -i :8081                  # macOS/Linux
```

### Airflow user already exists

**Cause:** Running `docker-compose up` multiple times without cleaning.

**Solution:**
```bash
# Reset Airflow database
docker-compose -f docker-compose.airflow.yml down -v
docker-compose -f docker-compose.airflow.yml up -d
```

### DAG not showing up in Airflow UI

**Cause:** DAG file is not in the correct location or has syntax errors.

**Solution:**

```bash
# Check if the DAG file exists in the mounted volume
docker exec commerce_airflow_scheduler ls /opt/airflow/dags/

# Test the DAG file for syntax errors
python -c "import ast; ast.parse(open('airflow/dags/commerce_lakehouse_dag.py').read())"
```

### `Broken DAG` in Airflow UI

**Cause:** Missing Python dependencies in the Airflow container.

**Solution:** Ensure `requirements-airflow.txt` includes all required packages:
```bash
# Check current packages in the Airflow container
docker exec commerce_airflow_scheduler pip list | grep -E "pandera|boto3"
```

---

## Python & Dependency Issues

### `ModuleNotFoundError: No module named 'pyspark'`

**Cause:** PySpark is not installed.

**Solution:**
```bash
pip install -r requirements.txt
python -c "import pyspark; print(pyspark.__version__)"
```

### `ModuleNotFoundError: No module named 'src'`

**Cause:** PYTHONPATH is not set correctly.

**Solution:**
```bash
# Set PYTHONPATH to project root
export PYTHONPATH=/path/to/DataLakehouse-Platform

# Or run from the project root directory
cd /path/to/DataLakehouse-Platform
```

### `pandera.errors.SchemaError: column 'X' not in DataFrame`

**Cause:** Schema mismatch between the validation schema and actual data.

**Solution:**
- Check if the column exists in the source data
- If the column was renamed during transformation, update the validation schema
- Run with `strict=False` in the schema definition if allowing extra columns

### `Missing required dependencies` when installing

**Cause:** Some system-level dependencies are missing.

**Solution:**
```bash
# Windows: Install Visual C++ Build Tools
# Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/

# macOS
brew install gcc

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
```

---

## Validation Issues

### `Bronze validation: Unexpected row count`

**Cause:** The bronze dataset has fewer rows than expected (minimum 100,000).

**Solution:**
- Ensure the historical dataset is not truncated
- Check if the dataset file was partially loaded
- Verify dataset integrity: `wc -l data/raw/historical/olist_ecommerce_dataset.csv`

### `Silver validation: Invalid order_status values found`

**Cause:** The dataset contains order status values not in the allowed set.

**Solution:** Check for unexpected status values:
```python
import pandas as pd
df = pd.read_parquet("data/silver/silver_orders.parquet")
print(df["order_status"].unique())
```
Expected values: `approved`, `canceled`, `created`, `delivered`, `invoiced`, `processing`, `shipped`, `unavailable`

### `Gold dataset validation failed: row count must be > 0`

**Cause:** Gold datasets are empty or not generated.

**Solution:**
```bash
# Check if Gold parquet files exist
ls -la data/gold/

# Run the Gold layer generation
python -m src.gold.gold_pipeline
```

### Validation report shows FAILED

**Cause:** One or more validation checks failed.

**Solution:** Check the validation report for details:
```bash
cat reports/data_quality/bronze_validation.json
cat reports/data_quality/silver_validation.json
cat reports/data_quality/gold_validation.json
```

---

## Permission Issues

### `Permission denied` when writing to `data/` directory

**Cause:** The application does not have write permissions for the data directory.

**Solution:**
```bash
# Ensure proper permissions
chmod -R 755 data/
```

### `Permission denied` when running scripts in Docker

**Cause:** File ownership mismatch between host and container.

**Solution:**
```bash
# Set proper permissions on mounted volumes
chmod -R 755 logs/ data/

# Or run container with current user UID
docker-compose run --user $(id -u):$(id -g) etl python main.py
```

---

## Still Having Issues?

If you've tried the solutions above and are still experiencing problems, please:

1. Check the pipeline logs in `logs/` directory
2. Run with debug logging: `LOG_LEVEL=DEBUG python main.py`
3. Open a [GitHub Issue](https://github.com/ojeshwigautam/DataLakehouse-Platform/issues)

---

> **Tip:** Most issues can be resolved by ensuring Java 17+ is installed, `JAVA_HOME` is set, and all Python dependencies are installed from `requirements.txt`.

