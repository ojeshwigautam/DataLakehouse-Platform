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
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORT_DIR = DATA_DIR / "exports"

# -------------------------------------------------
# Dataset Paths
# -------------------------------------------------

RAW_DATASET = RAW_DATA_DIR / "olist_ecommerce_dataset.csv"
BRONZE_DATASET = BRONZE_DIR / "bronze_orders.csv"

# -------------------------------------------------
# Log Directory
# -------------------------------------------------

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

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

