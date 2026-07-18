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

# ==========================================================
# Project Paths
# ==========================================================

# Gold
GOLD_PATH = PROJECT_ROOT / "data/gold"

DAILY_SALES_PATH = GOLD_PATH / "daily_sales.parquet"
MONTHLY_SALES_PATH = GOLD_PATH / "monthly_sales.parquet"
SELLER_PERFORMANCE_PATH = GOLD_PATH / "seller_performance.parquet"
PAYMENT_SUMMARY_PATH = GOLD_PATH / "payment_summary.parquet"
DELIVERY_SUMMARY_PATH = GOLD_PATH / "delivery_summary.parquet"
TOP_PRODUCTS_PATH = GOLD_PATH / "top_products.parquet"
TOP_STATES_PATH = GOLD_PATH / "top_states.parquet"


