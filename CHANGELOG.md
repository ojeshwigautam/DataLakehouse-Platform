# Changelog

All notable changes to the **Unified Commerce Lakehouse** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-07-18

### Added

#### Milestone 1 — Core Pipeline & Bronze Layer
- Data ingestion module with CSV loading and column cleanup
- Bronze layer creation with immutable raw Parquet storage
- Historical dataset loading from `data/raw/historical/`
- `FileHandler` abstraction supporting CSV and Parquet formats via `StorageFactory`
- Bronze validation with Pandera schema enforcement
- Validation report generation (JSON output to `reports/data_quality/`)

#### Milestone 2 — Silver Layer, Spark, & Validation
- Pandas-based Silver layer `create_silver_layer()` with:
  - Deduplication by `order_unique_id`
  - Text column trimming and standardization (city lowercase, state uppercase)
  - Timestamp conversion for all date columns
  - Negative numeric value filtering
- Apache Spark Silver pipeline `create_spark_silver()` with:
  - PySpark `clean_orders()` transformation (same logic as Pandas)
  - Spark session configuration with AQE, shuffle tuning, Snappy compression
  - Reconciliation report (Bronze vs. Silver comparison)
- Silver validation with Pandera (schema, row count, order status, duplicates)
- Spark DataFrame validation (`validate_silver_orders`) in `src/spark/validators.py`

#### Milestone 3 — Gold Layer, PostgreSQL, & Business Analytics
- Gold layer creation with 7 business aggregates:
  - `daily_sales.parquet` — revenue by day
  - `monthly_sales.parquet` — month-over-month trends
  - `top_products.parquet` — top 10 products by revenue
  - `top_states.parquet` — revenue by customer state
  - `payment_summary.parquet` — payment method breakdown
  - `seller_performance.parquet` — seller ranking (top 20)
  - `delivery_summary.parquet` — delivery time statistics
- Spark Gold pipeline with distributed aggregations
- Gold validation with Pandera (strict schema enforcement)
- PostgreSQL table loading with `to_sql` (replace mode)
- PostgreSQL table validation (existence + row counts)
- Pipeline audit table (`pipeline_audit`) with start/end/status tracking
- Analytics SQL queries in `sql/analytics_queries.sql`

#### Milestone 4 — CI/CD & Developer Experience
- GitHub Actions CI pipeline with 4 parallel jobs:
  - Lint & Format Check (Black, isort, Ruff)
  - Tests & Coverage (PySpark verification, pytest, HTML coverage)
  - Docker Image Build (with BuildKit cache)
  - Terraform Validation (fmt + validate)
- `requirements-dev.txt` for development dependencies
- `.pre-commit-config.yaml` with Black, isort, Ruff hooks
- `.coveragerc` configuration with 80% coverage threshold
- `pytest.ini` with coverage addopts
- Updated `.gitignore` for virtual environments, caches, coverage reports
- Docker Compose with PostgreSQL 18, ETL, Spark 4.2.0 services
- Airflow Docker Compose with webserver, scheduler, and init
- Terraform modules for AWS S3, IAM, EC2, Security Groups
- Developer workflow documentation with local CI check commands

#### Milestone 5 — Documentation & Repository Presentation
- Complete README rewrite with professional recruiter-quality content
- `docs/architecture.md` — full system architecture with Mermaid diagrams
- `docs/project-flow.md` — complete ETL workflow documentation
- `docs/setup-guide.md` — developer setup guide with all configurations
- `docs/benchmarks.md` — storage and performance benchmarks
- `docs/troubleshooting.md` — common issues and solutions
- `CHANGELOG.md` — semantic version history (this file)
- `CONTRIBUTING.md` — contribution guidelines
- `LICENSE` — MIT license
- Mermaid diagrams for architecture, ETL pipeline, folder structure, and pipeline flow

### Architecture & Infrastructure
- Incremental ingestion with checksum-based duplicate detection (`IncrementalLoader`)
- File discovery service (`FileDiscoverer`) with sorting and validation
- Checksum computation (SHA-256 / MD5) for idempotent processing
- Metadata schema in PostgreSQL with 4 tables:
  - `metadata.pipeline_runs` — run tracking
  - `metadata.processed_files` — checksum dedup registry
  - `metadata.watermarks` — incremental processing state
  - `metadata.pipeline_metrics` — per-stage execution metrics
- Structured logging with per-component log files (pipeline, bronze, silver, gold, postgres)
- Pipeline monitoring dashboard with success rate, duration, and stage metrics
- Execution timer utility for all pipeline stages
- AWS-ready architecture with Terraform infrastructure as code

### Dataset
- Brazilian Olist E-Commerce Public Dataset (Kaggle)
- 113,390 rows × 38 columns
- CSV → Parquet storage compression (53.58 MB → 20.45 MB, 61.86% reduction)
- 88.03% read speed improvement with Parquet over CSV

---

[1.0.0]: https://github.com/ojeshwigautam/DataLakehouse-Platform/releases/tag/v1.0.0

