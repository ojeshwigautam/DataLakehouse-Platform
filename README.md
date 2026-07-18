# 🚀 Unified Commerce Lakehouse Platform

[![Spark ETL CI](https://github.com/ojeshwigautam/DataLakehouse-Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/ojeshwigautam/DataLakehouse-Platform/actions/workflows/ci.yml)

> **A Production-Inspired End-to-End Data Engineering Platform implementing a Medallion (Bronze–Silver–Gold) Architecture with automated ETL pipelines, PostgreSQL integration, Apache Airflow orchestration, Docker containerization, pipeline monitoring, audit logging, and CI/CD automation.**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![Apache Airflow](https://img.shields.io/badge/Apache-Airflow-C01717?style=for-the-badge&logo=apacheairflow)
![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=githubactions)
![Pytest](https://img.shields.io/badge/Tested-Pytest-success?style=for-the-badge&logo=pytest)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

# 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Business Problem](#-business-problem)
- [Project Objectives](#-project-objectives)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Data Pipeline Workflow](#-data-pipeline-workflow)
- [Medallion Architecture](#-medallion-architecture)
- [Repository Structure](#-repository-structure)
- *(Technology Stack, Installation, Docker, Airflow, PostgreSQL, Testing, Monitoring, Roadmap and other sections continue below.)*

---

# 📌 Project Overview

Modern organizations generate massive amounts of transactional data every day. Transforming raw operational data into clean, reliable, and analytics-ready datasets requires scalable ETL pipelines, robust validation mechanisms, workflow orchestration, monitoring, and dependable storage.

The **Unified Commerce Lakehouse Platform** is a **production-inspired Data Engineering project** designed to simulate how modern data platforms process transactional data using a layered Medallion Architecture.

Starting from raw e-commerce records, the platform automates the complete ETL lifecycle:

- Ingests raw transactional datasets
- Preserves immutable source data
- Cleanses and validates records
- Applies business transformations
- Produces analytics-ready datasets
- Loads curated tables into PostgreSQL
- Tracks pipeline executions
- Monitors pipeline health
- Automates workflows using Apache Airflow
- Runs inside reproducible Docker environments

The project emphasizes modular design, maintainability, observability, reproducibility, and software engineering best practices commonly used in modern Data Engineering teams.

---

# 🎯 Business Problem

E-commerce businesses continuously generate transactional data from customers, orders, sellers, payments, deliveries, and products.

Raw operational data is typically:

- Distributed across multiple sources
- Inconsistent in formatting
- Contains duplicate records
- Contains missing values
- Difficult to analyze directly
- Unsuitable for BI dashboards
- Not optimized for reporting

Business teams require reliable datasets that support:

- Sales reporting
- Revenue analysis
- Product performance
- Seller performance
- Regional insights
- Payment analysis
- Delivery analytics

Without a structured ETL pipeline, organizations spend significant engineering effort repeatedly cleaning and transforming data before analysis.

---

# 🎯 Project Objectives

The primary objective of this project is to demonstrate how an end-to-end Data Engineering platform can transform raw operational data into trusted analytical datasets.

The project focuses on implementing:

✅ Layered Medallion Architecture

✅ Modular ETL pipeline

✅ Automated data ingestion

✅ Data validation framework

✅ Data cleaning and transformation

✅ Business aggregation logic

✅ PostgreSQL warehouse integration

✅ Pipeline execution monitoring

✅ Audit logging

✅ Workflow orchestration using Apache Airflow

✅ Docker-based reproducible deployment

✅ Automated testing

✅ CI/CD automation using GitHub Actions

---

# ✨ Key Features

## Data Engineering

- Medallion Architecture (Bronze → Silver → Gold)
- Modular ETL pipeline
- Configurable project structure
- Incremental ingestion framework
- Business-level aggregations
- Analytics-ready datasets

---

## Data Quality

- Missing value validation
- Duplicate detection
- Schema validation
- Dataset profiling
- Validation reporting

---

## Database Integration

- PostgreSQL integration
- Automatic table creation
- Batch loading
- Transaction handling
- SQLAlchemy ORM support

---

## Pipeline Observability

- Pipeline metrics
- Success rate monitoring
- Execution duration tracking
- Audit logging
- Pipeline statistics
- Structured logging

---

## Workflow Automation

- Apache Airflow DAG
- Scheduled execution
- Manual triggering
- Retry support
- Task orchestration

---

## DevOps

- Docker containers
- Docker Compose
- Environment configuration
- GitHub Actions CI
- Modular configuration

---

## Software Engineering

- Modular codebase
- Object-oriented design
- Configuration management
- Logging framework
- Unit testing
- Clean project structure

---

# 🏗 System Architecture

The platform follows a layered architecture inspired by enterprise Data Engineering systems.

```

┌────────────────────────────────────────────┐
│          Historical CSV Dataset            │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│          Data Ingestion Module             │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│            Bronze Layer                    │
│      Raw Immutable Dataset Storage         │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│        Data Validation Framework           │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│            Silver Layer                    │
│   Cleaning • Standardization • Processing  │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│             Gold Layer                     │
│      Business Aggregation & Analytics      │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│          PostgreSQL Warehouse              │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│ Pipeline Monitoring & Audit Logging        │
└────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────┐
│       Apache Airflow Orchestration         │
└────────────────────────────────────────────┘

```

---

# 🔄 Data Pipeline Workflow

The platform executes the following workflow during every pipeline run:

```

Historical Dataset

↓

Data Ingestion

↓

Bronze Layer

↓

Data Validation

↓

Silver Processing

↓

Business Transformations

↓

Gold Layer

↓

PostgreSQL Loading

↓

Pipeline Metrics

↓

Audit Logging

↓

Airflow Scheduling

```

Each stage is independently modular, allowing future extensions without affecting the remaining pipeline.

---

# 🥇 Medallion Architecture

The project follows the industry-standard **Bronze → Silver → Gold** architecture used in modern data lakehouse platforms.

---

## 🟤 Bronze Layer

Purpose:

Store raw immutable source data exactly as received.

Responsibilities:

- Preserve original records
- Maintain raw historical data
- Support reproducibility
- Enable debugging
- Act as single source of truth

No business transformations occur in this layer.

---

## ⚪ Silver Layer

Purpose:

Transform raw data into clean, standardized datasets.

Responsibilities:

- Data cleaning
- Missing value handling
- Duplicate removal
- Schema consistency
- Type conversions
- Validation
- Standardization

This layer produces trusted datasets suitable for downstream processing.

---

## 🟡 Gold Layer

Purpose:

Create analytics-ready datasets optimized for reporting and business intelligence.

Current Gold datasets include:

- Daily Sales
- Monthly Sales
- Top Products
- Top States
- Seller Performance
- Payment Summary
- Delivery Summary

These datasets are automatically loaded into PostgreSQL for analytical querying.

---

# 📂 Repository Structure

```text
DataLakehouse-Platform/
│
├── airflow/                 # Apache Airflow DAGs and configuration
├── architecture/            # System architecture diagrams
├── dashboards/              # Dashboard resources
├── data/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── processed/
│
├── docker/                  # Docker-related resources
├── docs/                    # Project documentation
├── logs/                    # Pipeline execution logs
├── notebooks/               # Exploratory notebooks
├── sql/                     # SQL scripts
├── src/
│   ├── bronze/
│   ├── config/
│   ├── database/
│   ├── gold/
│   ├── monitoring/
│   ├── pipeline/
│   ├── processing/
│   ├── utils/
│   └── validation/
│
├── terraform/               # Reserved for future cloud infrastructure
├── tests/                   # Unit and integration tests
│
├── .env.example
├── docker-compose.yml
├── docker-compose.airflow.yml
├── Dockerfile
├── Dockerfile.airflow
├── main.py
├── requirements.txt
└── README.md
```

---

## 📌 Current Implementation Status

### ✅ Implemented (Version 1.0)

- Medallion Architecture (Bronze → Silver → Gold)
- Automated ETL Pipeline
- PostgreSQL Integration
- Docker Containerization
- Apache Airflow Orchestration
- Pipeline Monitoring
- Pipeline Audit Logging
- GitHub Actions CI
- Unit Testing
- Incremental Processing Framework
- Structured Logging
- Modular Project Architecture

### 🚧 Planned for Version 2

- Apache Spark Processing
- Parquet Storage
- AWS S3 Data Lake
- Terraform Infrastructure
- Advanced Incremental Processing
- Data Quality Gates
- Cloud Deployment
- Production Monitoring Stack
