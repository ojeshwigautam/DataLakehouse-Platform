# 🚀 Unified Commerce Lakehouse Platform

> **Production-Inspired End-to-End Data Engineering Platform**

## Project Status

**Current Version:** v1.0 (Active Development)

This project demonstrates an end-to-end Medallion (Bronze → Silver →
Gold) architecture for e-commerce analytics using Python, PostgreSQL,
Docker, Apache Airflow, testing, monitoring, audit logging, and CI/CD.

## Implemented

-   Bronze, Silver, Gold architecture
-   Automated ETL
-   PostgreSQL integration
-   Docker & Docker Compose
-   Apache Airflow orchestration
-   Pipeline monitoring
-   Audit logging
-   Incremental processing framework
-   GitHub Actions
-   Pytest

## Planned (Version 2)

-   Apache Spark
-   Parquet
-   AWS S3
-   Terraform
-   Great Expectations

## Architecture

Raw Dataset ↓ Bronze ↓ Validation ↓ Silver ↓ Business Transformations ↓
Gold ↓ PostgreSQL ↓ Monitoring & Audit ↓ Apache Airflow

## Dataset

-   Brazilian Olist E-Commerce Dataset
-   113,390+ rows
-   38 columns

## Gold Tables

-   daily_sales
-   monthly_sales
-   payment_summary
-   seller_performance
-   top_products
-   top_states
-   delivery_summary

## Repository Structure

``` text
src/
  bronze/
  config/
  database/
  gold/
  monitoring/
  pipeline/
  processing/
  utils/
  validation/
```

## Author

Ojeshwi Gautam
