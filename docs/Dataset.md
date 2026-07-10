# Dataset Documentation

## Dataset Name
Brazilian E-Commerce Public Dataset by Olist

## Source
Kaggle - Olist Brazilian E-Commerce Public Dataset

## Business Domain
Retail / E-Commerce

## Purpose

This dataset serves as the historical transactional data source for the Unified Commerce Lakehouse project.

It contains information about:

- Customers
- Orders
- Order Items
- Products
- Sellers
- Payments
- Reviews
- Geolocation

The dataset will be processed through a Medallion Architecture consisting of Bronze, Silver, and Gold layers.

## Pipeline Flow

Historical Dataset
        ↓
Bronze Layer (Raw)
        ↓
Silver Layer (Cleaned & Validated)
        ↓
Gold Layer (Business Analytics)
        ↓
Power BI Dashboard

## Future Work

- Incremental data ingestion
- Data quality validation
- Airflow orchestration
- Spark transformations
- Cloud deployment