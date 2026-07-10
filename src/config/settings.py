from pathlib import Path

# -------------------------------------------------
# Project Root
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# -------------------------------------------------
# Data Directories
# -------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw" / "historical"
BRONZE_DIR = DATA_DIR / "bronze" / "historical"
SILVER_DIR = (DATA_DIR / "silver").resolve()
GOLD_DIR = DATA_DIR / "gold"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = DATA_DIR / "exports"

# -------------------------------------------------
# Dataset Paths
# -------------------------------------------------

RAW_DATASET = RAW_DATA_DIR / "olist_ecommerce_dataset.csv"
BRONZE_DATASET = BRONZE_DIR / "bronze_orders.csv"
SILVER_DATASET = SILVER_DIR / "silver_orders.csv"


# -------------------------------------------------
# Log Directory
# -------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# -------------------------------------------------
# Gold Layer Output Files
# -------------------------------------------------

GOLD_DAILY_SALES = GOLD_DIR / "daily_sales.csv"
GOLD_MONTHLY_SALES = GOLD_DIR / "monthly_sales.csv"
GOLD_TOP_PRODUCTS = GOLD_DIR / "top_products.csv"
GOLD_TOP_STATES = GOLD_DIR / "top_states.csv"
GOLD_PAYMENT_SUMMARY = GOLD_DIR / "payment_summary.csv"
GOLD_SELLER_PERFORMANCE = GOLD_DIR / "seller_performance.csv"
GOLD_DELIVERY_SUMMARY = GOLD_DIR / "delivery_summary.csv"


# -------------------------------------------------
# Create directories if missing
# -------------------------------------------------

for directory in [
    RAW_DATA_DIR,
    BRONZE_DIR,
    SILVER_DIR,
    GOLD_DIR,
    PROCESSED_DIR,
    EXPORT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


