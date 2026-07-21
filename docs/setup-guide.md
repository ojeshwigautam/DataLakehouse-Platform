# Developer Setup Guide

This guide provides step-by-step instructions for setting up the Unified Commerce Lakehouse development environment.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Repository Setup](#repository-setup)
- [Python Environment](#python-environment)
- [Java Setup (Spark)](#java-setup-spark)
- [PostgreSQL Setup](#postgresql-setup)
- [Docker Setup](#docker-setup)
- [Airflow Setup](#airflow-setup)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Running Tests](#running-tests)
- [Running CI Locally](#running-ci-locally)

---

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Core programming language |
| Java | 17+ | Apache Spark runtime |
| Docker Desktop | Latest | Containerized services |
| Git | Latest | Version control |
| PostgreSQL | 15+ | Warehouse (optional, Docker recommended) |

---

## Repository Setup

### Clone the Repository

```bash
git clone https://github.com/ojeshwigautam/DataLakehouse-Platform.git
cd DataLakehouse-Platform
```

---

## Python Environment

### Create Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Install Runtime Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas` — Data processing
- `numpy` — Numerical operations
- `pyarrow` — Parquet support
- `pyspark` — Apache Spark 4.0.0
- `SQLAlchemy` — Database ORM
- `psycopg2-binary` — PostgreSQL driver
- `boto3` — AWS SDK
- `python-dotenv` — Environment variables
- `pandera` — Data validation
- `psutil` — System monitoring

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:
- `black` — Code formatter
- `isort` — Import sorter
- `ruff` — Linter
- `pre-commit` — Git hooks

### Install Pre-commit Hooks

```bash
pre-commit install
```

This configures automatic formatting and linting checks before every commit.

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11+

# Check PySpark
python -c "import pyspark; print(f'PySpark {pyspark.__version__}')"

# Check Pandera
python -c "import pandera; print(f'Pandera {pandera.__version__}')"
```

---

## Java Setup (Spark)

Apache Spark requires Java 17 or later.

### Download and Install

**Option A: Eclipse Temurin (Recommended)**

1. Download from [Adoptium.net](https://adoptium.net/)
2. Choose Java 17 (LTS) for your operating system
3. Run the installer

**Option B: Oracle JDK**

1. Download from [Oracle.com](https://www.oracle.com/java/technologies/downloads/)
2. Choose Java 17 or later
3. Run the installer

### Set JAVA_HOME

```bash
# macOS / Linux (add to ~/.bashrc or ~/.zshrc)
export JAVA_HOME=/path/to/jdk-17
export PATH=$JAVA_HOME/bin:$PATH

# Windows (System Environment Variables)
# Set JAVA_HOME = C:\Program Files\Java\jdk-17
# Add %JAVA_HOME%\bin to PATH
```

### Verify Java

```bash
java -version
# Should output: openjdk version "17.x.x" ...
```

---

## PostgreSQL Setup

### Option A: Using Docker (Recommended)

PostgreSQL runs automatically via Docker Compose. The service is exposed on port **5433** (mapped to container port 5432) to avoid conflicts with local PostgreSQL installations.

```bash
docker compose up -d postgres
```

### Option B: Local Installation

If you prefer a local PostgreSQL installation:

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Create Database

```bash
# Using Docker
psql -h localhost -p 5433 -U postgres -c "CREATE DATABASE commerce_lakehouse;"

# Using local PostgreSQL (default port 5432)
psql -h localhost -U postgres -c "CREATE DATABASE commerce_lakehouse;"
```

### Create Metadata Schema and Tables

```bash
python -c "
from src.metadata.metadata_manager import MetadataManager
mgr = MetadataManager()
mgr.create_tables()
"
```

---

## Docker Setup

### Install Docker Desktop

Download from [docker.com](https://www.docker.com/products/docker-desktop/)

- **Windows:** Ensure WSL 2 is enabled
- **macOS:** Works with both Intel and Apple Silicon
- **Linux:** Follow distribution-specific instructions

### Verify Docker

```bash
docker --version
docker compose --version
```

### Main Services

The `docker-compose.yml` file defines three services:

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| `postgres` | `postgres:18` | 5433:5432 | Warehouse + metadata |
| `etl` | Custom | — | Runs ETL pipeline |
| `spark` | `apache/spark:4.2.0` | — | Spark processing |

```bash
# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f
```

---

## Airflow Setup

Airflow runs in a separate Docker Compose environment.

### Services

The `docker-compose.airflow.yml` defines:

| Service | Purpose | Port |
|---------|---------|------|
| `postgres` | Lakehouse database | 5433:5432 |
| `airflow-postgres` | Airflow metadata DB | — |
| `airflow-init` | DB migration + admin user | — |
| `airflow-webserver` | Web UI | 8081:8080 |
| `airflow-scheduler` | DAG execution | — |

### Start Airflow

```bash
docker compose -f docker-compose.airflow.yml up -d
```

### Access Airflow UI

1. Open `http://localhost:8081`
2. Login: `admin` / `admin123`
3. Enable the `commerce_lakehouse_etl` DAG

### Stop Airflow

```bash
docker compose -f docker-compose.airflow.yml down
```

### Reset Airflow

```bash
docker compose -f docker-compose.airflow.yml down -v
docker compose -f docker-compose.airflow.yml up -d
```

---

## Environment Variables

### Create `.env` File

```bash
cp .env.example .env
```

### Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port (`5433` for Docker) |
| `DB_NAME` | `commerce_lakehouse` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `METADATA_SCHEMA` | `metadata` | Metadata schema name |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Docker-Specific Variables

When running via Docker Compose, environment variables are auto-configured:

```yaml
# docker-compose.yml (etl service)
environment:
  DB_HOST: postgres
  DB_PORT: 5432
  DB_NAME: commerce_lakehouse
  DB_USER: postgres
  DB_PASSWORD: postgres
```

---

## Running Locally

### Run Full Pipeline

```bash
python main.py
```

Expected output:

```
======================================================================
  UNIFIED COMMERCE LAKEHOUSE — ETL PIPELINE v2.0
  Engine: Pandas + Spark | Storage: Parquet | Format: Snappy
======================================================================
Step 1/5: Loading raw dataset          ✓  113,390 rows
Step 2/5: Saving to Bronze             ✓  Parquet
Step 3/5: Validation                   ✓  Passed
Step 4/5: Silver — Cleaning            ✓  113,201 records
Step 5/5: Gold                         ✓  7 tables loaded
======================================================================
  PIPELINE COMPLETE ✓
======================================================================
```

### Run Incremental ETL

```bash
python -c "
from src.ingestion.incremental_loader import IncrementalLoader
loader = IncrementalLoader()
result = loader.run()
print(f'Files processed: {result.new_files_count}')
print(f'Rows loaded: {result.rows_loaded}')
"
```

### Run Specific Pipeline Stages

```bash
# Bronze layer only
python -m src.tasks.bronze_task

# Silver layer only
python -m src.tasks.silver_task

# Gold layer only
python -m src.tasks.gold_task

# PostgreSQL load only
python -m src.tasks.postgres_task
```

### Run Spark Pipeline

```bash
# Spark Silver
python -m src.spark.silver_pipeline

# Spark Gold
python -m src.spark.gold_pipeline
```

### Check Pipeline Status

```bash
python -c "
from src.monitoring.pipeline_monitor import PipelineMonitor
PipelineMonitor.print_dashboard()
"
```

---

## Running with Docker

### Build and Start

```bash
# Build images (first time or after dependency changes)
docker compose build

# Start all services in background
docker compose up -d
```

### Run ETL Pipeline

The ETL container runs `python main.py` by default and executes on start:

```bash
# Run with default command
docker compose up etl

# Override command
docker compose run etl python main.py
```

### Run Spark Inside Container

```bash
# Execute Spark Silver pipeline
docker compose exec spark python /workspace/src/spark/silver_pipeline.py

# Execute Spark Gold pipeline
docker compose exec spark python /workspace/src/spark/gold_pipeline.py
```

### Check Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f etl
docker compose logs -f postgres
docker compose logs -f spark
```

---

## Running Tests

### Full Test Suite

```bash
pytest tests/ -v
```

### With Coverage Report

```bash
pytest tests/ -v --cov=src --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the coverage report.

### Test Categories

```bash
# Unit tests
pytest tests/ -v -m "not regression"

# Regression tests
pytest tests/regression/ -v

# Specific test file
pytest tests/test_pipeline_execution.py -v

# Specific test function
pytest tests/test_pipeline_execution.py::test_pipeline_success -v
```

### Spark Tests

```bash
# Spark transformation tests
pytest tests/test_spark_transforms.py -v

# Spark validation tests
pytest tests/test_spark_validators.py -v

# Spark reconciliation tests
pytest tests/test_spark_reconciliation.py -v
```

### Validation Tests

```bash
pytest tests/test_bronze_validation.py -v
pytest tests/test_silver_validation.py -v
pytest tests/test_gold_validation.py -v
```

### Database Tests

```bash
pytest tests/test_postgres_connection.py -v
```

---

## Running CI Locally

Run the same checks that the GitHub Actions CI pipeline executes:

### 1. Formatting Check

```bash
black --check .
```

Auto-fix formatting issues:

```bash
black .
```

### 2. Import Order Check

```bash
isort --check-only --profile=black --line-length=88 .
```

Auto-fix import order:

```bash
isort --profile=black --line-length=88 .
```

### 3. Linting

```bash
ruff check .
```

Auto-fix lint issues:

```bash
ruff check . --fix
```

### 4. Tests with Coverage

```bash
pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-config=.coveragerc \
  -v
```

### 5. HTML Coverage Report

```bash
pytest tests/ \
  --cov=src \
  --cov-report=html \
  --cov-config=.coveragerc
```

### 6. Docker Build Verification

```bash
docker compose build
docker compose config --quiet && echo "✅ docker-compose.yml is valid"
```

### 7. Full CI Pipeline (One Command)

```bash
# Run all CI checks sequentially
black --check . && \
isort --check-only --profile=black --line-length=88 . && \
ruff check . && \
pytest tests/ -v --cov=src --cov-report=term-missing --cov-config=.coveragerc && \
docker compose build
```

