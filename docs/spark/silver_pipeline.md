# Spark Silver Pipeline

## Overview
The Spark **Silver** pipeline reads the **Bronze** orders dataset (Parquet), applies cleaning/standardization, validates the output, and writes the transformed dataset back to the Silver layer.

## Input dataset
- **Bronze path:** `data/bronze/historical/bronze_orders.parquet`

## Output dataset
- **Silver path:** `data/silver/silver_orders_spark.parquet`

## Cleaning steps (Silver)
Implemented in `src/spark/transforms.py` as `clean_orders(df)`:
1. Deduplicate by `order_unique_id`.
2. Trim whitespace on all string columns.
3. Standardize:
   - `customer_city`, `seller_city` -> lowercase
   - `customer_state`, `seller_state` -> uppercase
4. Convert timestamp columns to Spark timestamps.
5. Filter out invalid numeric values:
   - `price`, `payment_value`, `freight_value` must be `>= 0`

## Validation (pre-write)
Implemented in `src/spark/validators.py` as `validate_silver_orders(df)`:
- Row count must be > 0
- Required columns must exist
- No duplicate `order_unique_id`
- Critical columns are not entirely null

Validation failures raise clear exceptions before writing output.

## Spark optimizations
Configured in `src/spark/session.py`:
- Adaptive Query Execution enabled (`spark.sql.adaptive.enabled=true`)
- Tuned shuffle partitions (`spark.sql.shuffle.partitions`)
- Explicit Parquet compression codec (`spark.sql.parquet.compression.codec`)

## How to execute inside Docker
From the project root:

1. Build and start containers (if not already running):
   ```bash
   docker-compose up --build
   ```
2. Run the Silver pipeline script inside the container (example):
   ```bash
   python -m src.spark.silver_pipeline
   ```

(Actual command may vary depending on your container entrypoint/workflow.)

