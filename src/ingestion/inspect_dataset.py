# Allow running this script directly (python src/ingestion/inspect_dataset.py)
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.bronze.save_to_bronze import save_to_bronze  # noqa: E402

# Dataset path
from src.config.settings import BRONZE_DIR, RAW_DATASET  # noqa: E402
from src.ingestion.load_dataset import load_dataset  # noqa: E402
from src.monitoring.logger import get_logger  # noqa: E402
from src.processing.silver_pipeline import create_silver_layer  # noqa: E402
from src.processing.validate_dataset import validate_dataset  # noqa: E402

logger = get_logger("pipeline")

logger.info("=" * 60)
logger.info("UNIFIED COMMERCE LAKEHOUSE")
logger.info("Dataset Inspection")
logger.info("=" * 60)

# Read dataset
df = load_dataset(RAW_DATASET)


# Remove unwanted index column if present
if "Unnamed: 0" in df.columns:
    df.drop(columns=["Unnamed: 0"], inplace=True)

logger.info(f"Rows    : {df.shape[0]}")
logger.info(f"Columns : {df.shape[1]}")

logger.info("Column Names")
logger.info("-" * 60)
for column in df.columns:
    logger.info(column)

logger.info("Missing Values")
logger.info("-" * 60)
# Log missing values per column
missing = df.isnull().sum()
for col in df.columns:
    if missing[col] > 0:
        logger.info(f"  {col:<35} {missing[col]}")
logger.info(f"  Total missing values: {df.isnull().sum().sum()}")

logger.info("Dataset Information")
logger.info("-" * 60)
logger.info(f"Shape: {df.shape}")
logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

logger.info("First Five Records")
logger.info("-" * 60)
for i, row in df.head().iterrows():
    logger.info(f"Row {i}: {dict(row)}")

save_to_bronze(df, BRONZE_DIR)

validate_dataset(df)
create_silver_layer()
