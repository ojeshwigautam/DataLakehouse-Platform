import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# -------------------------------------------------
# Project Root
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# -------------------------------------------------
# Data Directories
# -------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw" / "historical"
INCREMENTAL_DATA_DIR = DATA_DIR / "raw" / "incremental"

BRONZE_DIR = DATA_DIR / "bronze" / "historical"
BRONZE_INCREMENTAL_DIR = DATA_DIR / "bronze" / "incremental"

SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"

PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_INCREMENTAL_DIR = PROCESSED_DIR / "incremental"

EXPORT_DIR = DATA_DIR / "exports"

# -------------------------------------------------
# Dataset Paths
# -------------------------------------------------

RAW_DATASET = RAW_DATA_DIR / "olist_ecommerce_dataset.csv"
BRONZE_DATASET = BRONZE_DIR / "bronze_orders.parquet"
SILVER_DATASET = SILVER_DIR / "silver_orders.parquet"


# -------------------------------------------------
# Log Directory
# -------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# PostgreSQL Connection Settings
# -------------------------------------------------

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "commerce_lakehouse")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# -------------------------------------------------
# Metadata Schema
# -------------------------------------------------

METADATA_SCHEMA = os.getenv("METADATA_SCHEMA", "metadata")

# -------------------------------------------------
# Logging Level
# -------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# -------------------------------------------------
# Gold Layer Output Files
# -------------------------------------------------

GOLD_DAILY_SALES = GOLD_DIR / "daily_sales.parquet"
GOLD_MONTHLY_SALES = GOLD_DIR / "monthly_sales.parquet"
GOLD_TOP_PRODUCTS = GOLD_DIR / "top_products.parquet"
GOLD_TOP_STATES = GOLD_DIR / "top_states.parquet"
GOLD_PAYMENT_SUMMARY = GOLD_DIR / "payment_summary.parquet"
GOLD_SELLER_PERFORMANCE = GOLD_DIR / "seller_performance.parquet"
GOLD_DELIVERY_SUMMARY = GOLD_DIR / "delivery_summary.parquet"


# -------------------------------------------------
# Create directories if missing
# -------------------------------------------------

for directory in [
    RAW_DATA_DIR,
    INCREMENTAL_DATA_DIR,
    BRONZE_DIR,
    BRONZE_INCREMENTAL_DIR,
    SILVER_DIR,
    GOLD_DIR,
    PROCESSED_DIR,
    PROCESSED_INCREMENTAL_DIR,
    EXPORT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
