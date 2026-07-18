from pathlib import Path

# ==========================================================
# Spark Application
# ==========================================================

APP_NAME = "Unified Commerce Lakehouse"

SPARK_MASTER = "local[*]"

SHUFFLE_PARTITIONS = "8"


PARQUET_COMPRESSION = "snappy"

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path("/workspace")

BRONZE_PATH = PROJECT_ROOT / "data/bronze/historical/bronze_orders.parquet"

SILVER_PATH = PROJECT_ROOT / "data/silver/silver_orders_spark.parquet"

