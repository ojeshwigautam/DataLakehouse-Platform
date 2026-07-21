<div align="center">

# 🏗️ Unified Commerce Lakehouse

### Production-Grade Medallion Data Lakehouse — Apache Spark · Docker · PostgreSQL · Airflow

[![Spark ETL CI](https://github.com/ojeshwigautam/DataLakehouse-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/ojeshwigautam/DataLakehouse-Platform/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-4.0.0-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Apache Airflow](https://img.shields.io/badge/Airflow-2.11-017CEE?style=flat-square&logo=apacheairflow&logoColor=white)](https://airflow.apache.org)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Pandera](https://img.shields.io/badge/Validation-Pandera-FF6B6B?style=flat-square)](https://pandera.readthedocs.io)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://terraform.io)
[![AWS S3](https://img.shields.io/badge/AWS-S3%20Ready-FF9900?style=flat-square&logo=amazons3&logoColor=white)](https://aws.amazon.com/s3)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-brightgreen?style=flat-square)](https://github.com/ojeshwigautam/DataLakehouse-Platform/actions)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000?style=flat-square)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)](#)

---

### 🎯 Built by [Ojeshwi Gautam](https://github.com/ojeshwigautam)
### 📍 LPU × Futurense Industry Internship 2026 — Data Platform & Pipeline Engineering

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Solution Architecture](#-solution-architecture)
- [Key Features](#-key-features)
- [Medallion Architecture](#-medallion-architecture)
- [ETL Workflow](#-etl-workflow)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
- [Running with Docker](#-running-with-docker)
- [Running with Airflow](#-running-with-airflow)
- [Running the ETL Pipeline](#-running-the-etl-pipeline)
- [Running Incremental ETL](#-running-incremental-etl)
- [Running Tests](#-running-tests)
- [Running CI Locally](#-running-ci-locally)
- [Monitoring](#-monitoring)
- [Validation Framework](#-validation-framework)
- [Metadata Management](#-metadata-management)
- [Performance Benchmarks](#-performance-benchmarks)
- [Project Roadmap](#-project-roadmap)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

---

## 📖 Project Overview

The **Unified Commerce Lakehouse** is a production-grade Data Engineering platform that implements the **Medallion Architecture** (Bronze → Silver → Gold) to process multi-channel retail transaction data through a fully automated, validated, and orchestrated pipeline.

| Attribute | Detail |
|-----------|--------|
| **Dataset** | Brazilian Olist E-Commerce (Kaggle) |
| **Records** | 113,390+ rows · 38 columns |
| **Architecture** | Medallion (Bronze / Silver / Gold) |
| **Processing** | Apache Spark (PySpark) + Pandas |
| **Storage** | Apache Parquet (Snappy compression) |
| **Warehouse** | PostgreSQL 15 |
| **Orchestration** | Apache Airflow 2.11 + Python ETL |
| **Containerization** | Docker Compose |
| **CI/CD** | GitHub Actions (4 parallel jobs) |
| **Infrastructure as Code** | Terraform (AWS) |
| **Status** | 🟢 Production Ready |

---

## 🎯 Problem Statement

Multi-channel retail businesses generate transactional data across websites, mobile apps, stores, and marketplaces — each in different formats with inconsistent schemas and varying data quality. Organizations struggle with:

- **No single source of truth** across fragmented data sources
- **Duplicate records, null values, and schema mismatches** in raw data
- **No historical traceability** when transformations overwrite source data
- **Manual pipelines** with no failure recovery or idempotency guarantees
- **Inability to answer business questions**: daily revenue, top products, regional performance, seller rankings, delivery KPIs

### Solution

This platform solves these challenges by implementing a **Medallion Data Lakehouse** that:

1. Preserves raw data immutably (Bronze)
2. Cleans and standardizes via distributed processing (Silver)
3. Creates business-ready analytics tables (Gold)
4. Validates at every layer to ensure data quality
5. Automates the entire workflow with Airflow orchestration
6. Tracks everything via metadata and audit logging

---

## 🏛️ Solution Architecture

```mermaid
flowchart TB
    subgraph Sources["📦 DATA SOURCES"]
        CSV[("Olist E-Commerce<br/>CSV · 113,390 rows")]
        INCR[("Incremental<br/>Parquet Files")]
    end

    subgraph Ingestion["⬇️ INGESTION"]
        direction TB
        FD[File Discovery<br/><code>FileDiscoverer</code>]
        CHK[Checksum Dedup<br/><code>SHA-256</code>]
        IL[Incremental Loader<br/><code>IncrementalLoader</code>]
    end

    subgraph Bronze["🥉 BRONZE LAYER"]
        B_SAVE[Immutable Raw Copy<br/><code>save_to_bronze</code>]
        B_VALID[Pandera Validation<br/>Schema · Nulls · Ranges]
        B_PARQUET[("Parquet · Snappy<br/>Partitioned")]
    end

    subgraph Silver["🥈 SILVER LAYER"]
        S_PANDAS[Pandas Pipeline<br/>Dedup · Clean · Standardize]
        S_SPARK[Spark Pipeline<br/>Distributed ETL · AQE]
        S_VALID[Validation<br/>Pandera + Spark Validators]
        S_PARQUET[("Cleaned Parquet<br/>Deduplicated")]
    end

    subgraph Gold["🥇 GOLD LAYER"]
        G_PANDAS[7 Business Aggregations<br/><code>gold_pipeline</code>]
        G_SPARK[Spark Gold<br/>Distributed Aggregations]
        G_VALID[Strict Schema Validation<br/>7 Gold Datasets]
        G_TABLES[("7 Analytics Tables<br/>Parquet")]
    end

    subgraph Warehouse["🗄️ WAREHOUSE & ANALYTICS"]
        PG_LOAD[PostgreSQL Loader<br/><code>load_gold_tables</code>]
        PG[(PostgreSQL 15<br/>commerce_lakehouse)]
        QUERIES[Analytics Queries<br/>SQL · Power BI]
    end

    subgraph Orchestration["⚙️ ORCHESTRATION"]
        PIPELINE[Python ETL Pipeline<br/><code>etl_pipeline.py</code>]
        DAG[Airflow DAG<br/><code>commerce_lakehouse_dag</code>]
        DOCKER[Docker Compose<br/>PostgreSQL · Spark · ETL · Airflow]
        CI[GitHub Actions CI/CD<br/>Lint · Test · Build · Deploy]
    end

    subgraph Observability["📊 OBSERVABILITY"]
        LOG[Structured Logging<br/>6 Component Loggers]
        METRICS[Pipeline Metrics<br/>Per-stage Execution]
        MONITOR[Monitoring Dashboard<br/>PipelineMonitor]
        AUDIT[Pipeline Audit<br/>Run ID · Duration · Status]
    end

    subgraph Metadata["📝 METADATA"]
        MM[MetadataManager<br/>4 PostgreSQL Tables]
        FT[FileTracker<br/>Checksum Registry]
        WM[WatermarkManager<br/>Incremental State]
    end

    subgraph Infra["☁️ INFRASTRUCTURE"]
        TF[Terraform<br/>AWS · S3 · IAM · EC2]
        S3[(AWS S3<br/>Cloud Storage)]
    end

    %% Data flow
    CSV --> FD
    INCR --> FD
    FD --> CHK
    CHK --> IL
    IL --> B_SAVE

    B_SAVE --> B_PARQUET
    B_PARQUET --> B_VALID

    B_PARQUET --> S_PANDAS
    B_PARQUET --> S_SPARK
    S_PANDAS --> S_VALID
    S_SPARK --> S_VALID
    S_VALID --> S_PARQUET

    S_PARQUET --> G_PANDAS
    S_PARQUET --> G_SPARK
    G_PANDAS --> G_VALID
    G_SPARK --> G_VALID
    G_VALID --> G_TABLES

    G_TABLES --> PG_LOAD
    PG_LOAD --> PG
    PG --> QUERIES

    %% Orchestration
    PIPELINE --> B_SAVE
    DAG --> PIPELINE
    CI --> DOCKER

    %% Metadata
    IL --> FT
    IL --> WM
    PIPELINE --> MM
    PIPELINE --> AUDIT

    %% Monitoring
    PIPELINE --> LOG
    PIPELINE --> METRICS
    METRICS --> MONITOR
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Medallion Architecture** | Bronze / Silver / Gold separation of concerns |
| **Dual Processing** | Pandas (local) + Apache Spark (distributed) |
| **Incremental Ingestion** | SHA-256 checksum dedup, watermark tracking, idempotent |
| **Data Validation** | Pandera schemas at every layer + Spark validators |
| **Pipeline Audit** | Every run logged with run_id, duration, row counts, status |
| **Structured Logging** | Per-component log files (pipeline, bronze, silver, gold, postgres) |
| **Airflow Orchestration** | DAG with branch detection, 10 stages, daily schedule |
| **PostgreSQL Warehouse** | 7 indexed analytics tables |
| **Containerized** | Docker Compose for ETL, Spark, PostgreSQL, Airflow |
| **AWS Ready** | Terraform IaC for S3, IAM, EC2 |
| **CI/CD Automation** | GitHub Actions with lint, test, Docker build, Terraform validate |
| **80%+ Test Coverage** | Unit, integration, and regression tests |
| **Parquet Storage** | Snappy compression, columnar format |
| **Power BI Integration** | Dashboard-ready data in PostgreSQL |

---

## 🏗️ Medallion Architecture

### 🥉 Bronze — Immutable Raw Zone

Stores data **exactly as received** — no transformations, no modifications.

- **Input:** Raw CSV (113,390 rows) + incremental Parquet batches
- **Storage:** Parquet with Snappy compression (`data/bronze/historical/`)
- **Validation:** Pandera schema — required columns, non-null, positive values
- **Purpose:** Source of truth for reprocessing, audit trail, compliance

### 🥈 Silver — Cleaned & Standardized Zone

Applies data quality transformations using **both Pandas and Apache Spark**.

- **Deduplication:** By `order_unique_id` or full row
- **Standardization:** City → lowercase, State → uppercase, timestamps → datetime
- **Cleaning:** String trimming, negative value filtering
- **Validation:** Pandera + Spark validators (required columns, allowed values, no duplicates)
- **Storage:** `data/silver/silver_orders.parquet`

### 🥇 Gold — Business Analytics Zone

Aggregates clean Silver data into **7 business-ready analytics tables**.

| Table | Business Question | Key Metrics |
|-------|-------------------|-------------|
| `daily_sales` | How much revenue did we make each day? | total_orders, total_revenue, avg_order_value |
| `monthly_sales` | What are the month-over-month trends? | MoM growth, revenue_per_customer |
| `top_products` | Which products drive the most revenue? | revenue_rank, units_sold, freight_impact |
| `top_states` | Which states contribute the most? | revenue_share, unique_customers |
| `payment_summary` | How do customers prefer to pay? | transaction_share, avg_installments |
| `seller_performance` | Which sellers perform best? | performance_tier, avg_revenue |
| `delivery_summary` | How fast do we deliver? | avg_delivery_days, late_rate |

---

## 🔄 ETL Workflow

```mermaid
flowchart LR
    RAW[Raw CSV Files] --> DISCOVER[File Discovery<br/><code>FileDiscoverer</code>]
    DISCOVER --> CHECKSUM[Checksum<br/><code>SHA-256</code>]
    CHECKSUM --> META{Already<br/>Processed?}
    META -->|No| BRONZE[Bronze Layer<br/>Immutable Parquet]
    META -->|Yes| SKIP[⏭️ Skip]
    BRONZE --> B_VALID[Bronze Validation<br/>Pandera Schema]
    B_VALID --> SILVER[Silver Layer<br/>Pandas / Spark]
    SILVER --> S_VALID[Silver Validation<br/>Pandera + Spark]
    S_VALID --> GOLD[Gold Layer<br/>7 Business Tables]
    GOLD --> G_VALID[Gold Validation<br/>Strict Schemas]
    G_VALID --> PG[PostgreSQL<br/>Warehouse]
    PG --> PG_VALID[PG Validation<br/>Table Existence]
    PG_VALID --> ANALYTICS[📊 Analytics<br/>SQL · Power BI]

    style BRONZE fill:#cd7f32,color:#fff
    style SILVER fill:#c0c0c0,color:#000
    style GOLD fill:#ffd700,color:#000
```

### Pipeline Stages (Airflow DAG)

| Stage | Task | Module | Duration |
|-------|------|--------|----------|
| 1 | Discover Incremental Files | `file_discovery.FileDiscoverer` | ~0.1s |
| 2 | Incremental Loader | `incremental_loader.IncrementalLoader` | ~0.5s |
| 3 | Bronze ETL | `tasks.bronze_task` | ~2.0s |
| 4 | Bronze Validation | `tasks.bronze_validation_task` | ~0.3s |
| 5 | Silver ETL | `tasks.silver_task` | ~2.0s |
| 6 | Silver Validation | `tasks.silver_validation_task` | ~0.3s |
| 7 | Gold ETL | `tasks.gold_task` | ~1.5s |
| 8 | Gold Validation | `tasks.gold_validation_task` | ~0.2s |
| 9 | PostgreSQL Load | `tasks.postgres_task` | ~2.0s |
| 10 | PostgreSQL Validation | `tasks.postgres_validation_task` | ~0.3s |
| — | Metadata Update | `MetadataManager` | ~0.2s |

---

## 🛠️ Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Core ETL, orchestration, validation |
| **Language** | SQL | — | Analytics queries |
| **Distributed Processing** | Apache Spark (PySpark) | 4.0.0 | Silver/Gold distributed ETL |
| **Data Processing** | Pandas | 2.2+ | Local ETL pipeline |
| **Columnar Storage** | Apache Parquet | — | Efficient compressed storage |
| **Warehouse** | PostgreSQL | 15 | Gold layer + metadata |
| **Validation** | Pandera | 0.20+ | Schema and data quality |
| **Orchestration** | Apache Airflow | 2.11 | DAG scheduling and execution |
| **Containerization** | Docker Compose | Latest | Service orchestration |
| **CI/CD** | GitHub Actions | — | Automated testing and build |
| **Infrastructure as Code** | Terraform | 1.7+ | AWS resource provisioning |
| **Cloud Storage** | AWS S3 | — | Cloud-ready storage layer |
| **Object-Relational Mapping** | SQLAlchemy | 2.0+ | PostgreSQL connection |
| **Data Visualization** | Power BI | — | Business dashboards |
| **Code Quality** | Black / isort / Ruff | Latest | Formatting, imports, linting |
| **Testing** | pytest | Latest | Unit, integration, regression |
| **Environment** | python-dotenv | 1.0+ | Configuration management |

---

## 📁 Repository Structure

```mermaid
graph TD
    ROOT[DataLakehouse-Platform/] --> AIRFLOW[airflow/]
    ROOT --> DATA[data/]
    ROOT --> DOCS[docs/]
    ROOT --> SCRIPTS[scripts/]
    ROOT --> SQL[sql/]
    ROOT --> SRC[src/]
    ROOT --> TERRAFORM[terraform/]
    ROOT --> TESTS[tests/]
    ROOT --> ROOT_FILES[docker-compose.yml<br/>Dockerfile<br/>main.py<br/>requirements.txt<br/>README.md]

    SRC --> INGESTION[ingestion/]
    SRC --> BRONZE[bronze/]
    SRC --> SILVER[processing/]
    SRC --> GOLD[gold/]
    SRC --> SPARK[spark/]
    SRC --> VALIDATION[validation/]
    SRC --> DATABASE[database/]
    SRC --> METADATA[metadata/]
    SRC --> MONITORING[monitoring/]
    SRC --> PIPELINE[pipeline/]
    SRC --> STORAGE[storage/]
    SRC --> TASKS[tasks/]
    SRC --> CONFIG[config/]
    SRC --> UTILS[utils/]

    DATA --> RAW[raw/]
    DATA --> BRONZE_DATA[bronze/]
    DATA --> SILVER_DATA[silver/]
    DATA --> GOLD_DATA[gold/]

    TESTS --> UNIT[tests/]
    TESTS --> REGRESSION[regression/]
```

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/ingestion/` | File discovery, checksum, incremental loading |
| `src/bronze/` | Bronze layer creation |
| `src/processing/` | Silver layer (Pandas) — dedup, clean, standardize |
| `src/gold/` | Gold layer — 7 business aggregations |
| `src/spark/` | Spark session, transforms, validators, reconciliation |
| `src/validation/` | Pandera schemas for Bronze, Silver, Gold |
| `src/database/` | PostgreSQL connection, table loading, validation |
| `src/metadata/` | Pipeline runs, file tracking, watermarks |
| `src/monitoring/` | Logging, metrics, execution timer |
| `src/pipeline/` | ETL orchestration |
| `src/storage/` | FileHandler abstraction (CSV/Parquet) |
| `src/tasks/` | Airflow task wrappers |
| `terraform/` | AWS IaC — S3, IAM, EC2, Security Groups |
| `tests/` | Unit, integration, and regression tests |
| `airflow/dags/` | Airflow DAG definitions |
| `sql/` | PostgreSQL analytics queries |

---

## 🚀 Getting Started

### Prerequisites

| Dependency | Version | Installation |
|-----------|---------|--------------|
| Python | 3.11+ | [python.org](https://python.org) |
| Java | 17+ | [adoptium.net](https://adoptium.net) |
| Docker Desktop | Latest | [docker.com](https://docker.com) |
| Git | Latest | [git-scm.com](https://git-scm.com) |

### Clone and Set Up

```bash
# Clone the repository
git clone https://github.com/ojeshwigautam/DataLakehouse-Platform.git
cd DataLakehouse-Platform

# Create virtual environment
python -m venv venv

# Activate it
# macOS/Linux: source venv/bin/activate
# Windows:     venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Configure environment
cp .env.example .env
# Edit .env with your credentials (defaults work for Docker)
```

### Set Java for Spark

```bash
# macOS/Linux
export JAVA_HOME=/path/to/jdk-17
export PATH=$JAVA_HOME/bin:$PATH

# Windows (System Environment Variables)
# Set JAVA_HOME = C:\Program Files\Java\jdk-17
# Add %JAVA_HOME%\bin to PATH

# Verify
java -version  # Must show 17.x.x
```

---

## 🐳 Running with Docker

### Start Core Services

```bash
# Build and start all services
docker compose up -d

# Verify services are running
docker compose ps

# View logs
docker compose logs -f
```

**Services started:**

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| PostgreSQL | `commerce_lakehouse_postgres` | **5433:5432** | Warehouse + metadata |
| ETL | `commerce_lakehouse_etl` | — | Runs `python main.py` |
| Spark | `commerce_spark` | — | Spark processing (kept alive) |

> **Note:** PostgreSQL is exposed on port **5433** to avoid conflicts with local PostgreSQL installations.

### Run ETL Pipeline in Docker

```bash
# The ETL container runs main.py automatically on start
docker compose up etl

# Or run explicitly
docker compose run etl python main.py
```

### Run Spark in Docker

```bash
# Spark Silver pipeline
docker compose exec spark python /workspace/src/spark/silver_pipeline.py

# Spark Gold pipeline
docker compose exec spark python /workspace/src/spark/gold_pipeline.py
```

### Connect to PostgreSQL

```bash
docker compose exec postgres psql -U postgres -d commerce_lakehouse

# Or from host machine
psql -h localhost -p 5433 -U postgres -d commerce_lakehouse
```

---

## 🌬️ Running with Airflow

### Start Airflow Services

```bash
docker compose -f docker-compose.airflow.yml up -d
```

This starts 5 services:
- `postgres` — Lakehouse database (port 5433)
- `airflow-postgres` — Airflow metadata database
- `airflow-init` — Runs DB migration + creates admin user
- `airflow-webserver` — Web UI on **port 8081**
- `airflow-scheduler` — DAG execution

### Access Airflow UI

1. Open [http://localhost:8081](http://localhost:8081)
2. Login: `admin` / `admin123`
3. Find the `commerce_lakehouse_etl` DAG
4. Click **"Trigger DAG"** to run manually

### Stop Airflow

```bash
docker compose -f docker-compose.airflow.yml down

# Full reset (removes volumes)
docker compose -f docker-compose.airflow.yml down -v
```

---

## ⚡ Running the ETL Pipeline

### Full Pipeline

```bash
python main.py
```

Expected output:

```
======================================================================
  UNIFIED COMMERCE LAKEHOUSE — ETL PIPELINE
  Engine: Pandas + Spark | Storage: Parquet | Format: Snappy
======================================================================
  Started : 2026-07-18 10:00:00
======================================================================
STEP 2/9 : Bronze Layer              ✓  113,390 rows → Parquet
STEP 3/9 : Bronze Validation         ✓  Pandera Passed
STEP 4/9 : Silver Layer              ✓  113,201 records
STEP 5/9 : Silver Validation         ✓  Pandera Passed
STEP 6/9 : Gold Layer                ✓  7 tables created
STEP 7/9 : Gold Validation           ✓  All Passed
STEP 8/9 : PostgreSQL                ✓  7 tables loaded
STEP 9/9 : PostgreSQL Validation     ✓  All tables verified
Incremental Data Ingestion          ✓  0 batches
======================================================================
  PIPELINE SUMMARY
======================================================================
Raw Dataset        : olist_ecommerce_dataset.csv
Bronze Dataset     : bronze_orders.parquet
Silver Dataset     : silver_orders.parquet
Gold Datasets Generated : 7
PostgreSQL Tables Loaded  : 7
Execution Time     : 0:00:11.24
Pipeline Status    : SUCCESS
======================================================================
```

### Run Individual Stages

```bash
# Bronze only
python -m src.tasks.bronze_task

# Silver only
python -m src.tasks.silver_task

# Gold only
python -m src.tasks.gold_task

# PostgreSQL load only
python -m src.tasks.postgres_task
```

---

## 📥 Running Incremental ETL

The incremental processing pipeline ensures **idempotent** data ingestion — running the same batch twice produces identical results.

```mermaid
flowchart LR
    A[New File Arrives] --> B[Compute SHA-256]
    B --> C{Checksum<br/>in Database?}
    C -->|No| D[Load & Transform]
    C -->|Yes| E[Skip — Already<br/>Processed]
    D --> F[Append to Bronze]
    F --> G[Update Metadata<br/>FileTracker + Watermark]
```

### Process Incremental Files

```python
from src.ingestion.incremental_loader import IncrementalLoader

loader = IncrementalLoader()
result = loader.run()

print(f"Files discovered: {result.total_files_discovered}")
print(f"New files processed: {result.new_files_count}")
print(f"Rows loaded: {result.rows_loaded}")
print(f"Status: {result.status}")
```

### Key Guarantees

| Feature | Implementation |
|---------|---------------|
| **Duplicate detection** | SHA-256 checksums stored in `metadata.processed_files` |
| **Idempotency** | Same file + content always skipped |
| **Watermark tracking** | Last processed file/timestamp stored in `metadata.watermarks` |
| **Bulk loading** | Merges with existing Bronze incremental Parquet |

---

## 🧪 Running Tests

### Full Test Suite

```bash
pytest tests/ -v
```

### With Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Categories

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/ -v -m "not regression"

# Regression tests
pytest tests/regression/ -v

# Specific test file
pytest tests/test_bronze_validation.py -v
pytest tests/test_silver_validation.py -v
pytest tests/test_gold_validation.py -v
pytest tests/test_spark_transforms.py -v
pytest tests/test_incremental_loader.py -v

# Pipeline execution
pytest tests/test_pipeline_execution.py -v
```

### Spark Tests

```bash
pytest tests/test_spark_transforms.py -v
pytest tests/test_spark_validators.py -v
pytest tests/test_spark_gold_transforms.py -v
pytest tests/test_spark_reconciliation.py -v
```

### Coverage Configuration (`.coveragerc`)

- **Minimum coverage:** 80%
- **Source:** `src/`
- **Excludes:** `__init__.py`, migrations, tests, scripts, notebooks

---

## 🔧 Running CI Locally

Run the same checks that the GitHub Actions pipeline executes:

```bash
# 1. Formatting check (Black)
black --check .

# 2. Import order (isort)
isort --check-only --profile=black --line-length=88 .

# 3. Linting (Ruff)
ruff check .

# 4. Tests with coverage
pytest tests/ \
  --cov=src \
  --cov-report=term-missing \
  --cov-config=.coveragerc \
  -v

# 5. Docker build verification
docker compose build
docker compose config --quiet && echo "✅ Valid"
```

### CI Pipeline (GitHub Actions)

```mermaid
flowchart LR
    PUSH[Push / PR] --> LINT[Lint & Format<br/>Black · isort · Ruff]
    LINT --> TEST[Tests & Coverage<br/>PySpark · pytest · 80%+]
    TEST --> DOCKER[Docker Build<br/>ETL Image · Compose Check]
    TEST --> TF[Terraform Validate<br/>fmt · validate]
    DOCKER --> PASS[✅ CI Passes]
    TF --> PASS
```

The CI pipeline runs on every push to `main`/`develop` and on pull requests.

---

## 📊 Monitoring

### Structured Logging

The platform writes per-component logs to `logs/`:

| Logger | File | Component |
|--------|------|-----------|
| `pipeline` | `logs/pipeline.log` | Main orchestration |
| `bronze` | `logs/bronze.log` | Bronze layer operations |
| `silver` | `logs/silver.log` | Silver layer operations |
| `gold` | `logs/gold.log` | Gold layer operations |
| `postgres` | `logs/postgres.log` | PostgreSQL operations |
| `airflow` | `logs/airflow.log` | Airflow DAG operations |

### Monitoring Dashboard

```bash
python -c "
from src.monitoring.pipeline_monitor import PipelineMonitor
PipelineMonitor.print_dashboard()
"
```

Output:
```
======================================================================
  PIPELINE MONITORING DASHBOARD
======================================================================
SUMMARY
  Total Runs               : 15
  Successful Runs          : 14
  Failed Runs              : 1
  Success Rate             : 93.33%
  Avg Duration             : 11.24s
  Total Incremental Batches: 3

LATEST RUN
  Run ID      : a1b2c3d4-...
  Pipeline    : Unified Commerce Lakehouse ETL
  Status      : SUCCESS
  Started     : 2026-07-18 10:00:00
  Completed   : 2026-07-18 10:00:11
  Duration    : 11.24s
```

### Pipeline Audit

Every execution is recorded in the `pipeline_audit` table:

```sql
SELECT run_id, status, execution_time_seconds, incremental_batches
FROM pipeline_audit
ORDER BY start_time DESC
LIMIT 5;
```

---

## ✅ Validation Framework

### Multi-Layer Validation

```mermaid
flowchart TB
    subgraph Bronze["🥉 BRONZE VALIDATION"]
        B1[Pandera Schema<br/>Required Columns]
        B2[Non-null Constraints]
        B3[Positive Numeric Values]
        B4[Min Row Count: 100k+]
    end

    subgraph Silver["🥈 SILVER VALIDATION"]
        S1[Pandera Schema]
        S2[Row Count ≥ 100k]
        S3[Allowed Order Statuses<br/>8 Valid Values]
        S4[Zero Duplicates]
        S5[Spark Validators<br/>Critical Nulls · Duplicate IDs]
    end

    subgraph Gold["🥇 GOLD VALIDATION"]
        G1[Strict Pandera Schema<br/>Dataset-specific Columns]
        G2[Non-null Dimensions]
        G3[Revenue ≥ 0]
        G4[Spark Gold Validators<br/>Row Count · Required Cols]
    end

    subgraph Database["🗄️ POSTGRESQL VALIDATION"]
        D1[7 Tables Exist]
        D2[Non-zero Row Counts]
    end

    Bronze --> Silver
    Silver --> Gold
    Gold --> Database
```

### Validation Reports

Results are saved as JSON to `reports/data_quality/`:

```json
{
  "layer": "bronze",
  "status": "PASSED",
  "message": "Bronze validation passed.",
  "timestamp": "2026-07-18T10:00:05"
}
```

---

## 📝 Metadata Management

The metadata system uses PostgreSQL with a dedicated `metadata` schema:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `metadata.pipeline_runs` | Track every pipeline execution | `run_id`, `status`, `duration_seconds`, `rows_processed` |
| `metadata.processed_files` | Checksum-based duplicate prevention | `file_name`, `checksum` (SHA-256), `status` |
| `metadata.watermarks` | Track last processed position | `pipeline_name`, `last_processed_file`, `last_processed_timestamp` |
| `metadata.pipeline_metrics` | Per-stage execution metrics | `stage`, `duration_seconds`, `rows_processed`, `status` |

---

## 📈 Performance Benchmarks

| Metric | CSV | Parquet | Improvement |
|--------|-----|---------|-------------|
| **File Size** | 53.58 MB | 20.45 MB | **61.86% reduction** |
| **Read Speed** | 1.7207 sec | 0.2076 sec | **88.03% faster** |
| **Memory Usage** | 75.89 MB | 75.03 MB | **1.15% reduction** |

**Full Pipeline Runtime:** ~11.24 seconds (Baseline v1.0)

---

## 🗺️ Project Roadmap

```mermaid
gantt
    title Project Roadmap
    dateFormat  YYYY-MM-DD
    axisFormat  %Y Q%q

    section Sprint 0
    Repository & Architecture Setup    :done, s0, 2026-01-01, 30d

    section Sprint 1
    Bronze Layer & Docker               :done, s1, after s0, 30d
    Data Ingestion                      :done, after s0, 30d

    section Sprint 2
    Apache Spark Integration            :done, s2, after s1, 30d
    Silver Layer & Validation           :done, after s1, 30d

    section Sprint 3
    Gold Layer & PostgreSQL             :done, s3, after s2, 30d
    Business Analytics Tables           :done, after s2, 30d

    section Sprint 4
    Airflow Orchestration               :done, s4, after s3, 30d
    CI/CD & Terraform                   :done, after s3, 30d

    section Sprint 5
    Documentation & Polish              :done, s5, after s4, 30d
    Power BI Integration                :done, after s4, 30d
```

### Future Enhancements

- [ ] Migrate to **AWS Glue** for fully managed Spark execution
- [ ] Add **Apache Iceberg** for ACID transactions on S3
- [ ] Implement real-time ingestion with **Apache Kafka**
- [ ] Add **dbt** for transformation lineage and documentation
- [ ] Deploy **Grafana** dashboards for pipeline monitoring
- [ ] Add **Great Expectations** for enhanced data quality
- [ ] Implement **data contracts** with schema registry
- [ ] Add **Apache Hudi** for incremental processing on S3

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

```bash
# Fork → clone → branch → commit → PR

git checkout -b feat/your-feature
git commit -m "feat(silver): add schema evolution handling"
git push origin feat/your-feature
```

**Guidelines:**
- Follow [Conventional Commits](https://www.conventionalcommits.org/)
- All PRs must pass CI before merge
- Add tests for new functionality
- Maintain 80%+ test coverage

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle
- **Institution:** LPU × Futurense Industry Internship 2026 — Data Platform & Pipeline Engineering
- **Technologies:** Apache Spark, Apache Airflow, PostgreSQL, Docker, Terraform

---

<div align="center">

### Built with ❤️ by [Ojeshwi Gautam](https://github.com/ojeshwigautam)

[![LinkedIn](https://img.shields.io/badge/Let's%20Connect-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ojeshwi-gautam)
[![GitHub](https://img.shields.io/badge/Follow%20Me-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/ojeshwigautam)
[![Email](https://img.shields.io/badge/Email%20Me-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:ojeshwi.gautam@example.com)

> ⭐ Star this repository if you find it useful for understanding production-grade Data Engineering patterns!

</div>

