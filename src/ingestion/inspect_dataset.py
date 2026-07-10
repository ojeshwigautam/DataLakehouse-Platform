from pathlib import Path

# Allow running this script directly (python src/ingestion/inspect_dataset.py)
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.load_dataset import load_dataset
from src.bronze.save_to_bronze import save_to_bronze
from src.processing.validate_dataset import validate_dataset


# Dataset path
from src.config.settings import RAW_DATASET, BRONZE_DIR


print("=" * 60)
print("UNIFIED COMMERCE LAKEHOUSE")
print("Dataset Inspection")
print("=" * 60)

# Read dataset
df = load_dataset(RAW_DATASET)


# Remove unwanted index column if present
if "Unnamed: 0" in df.columns:
    df.drop(columns=["Unnamed: 0"], inplace=True)

print(f"\nRows    : {df.shape[0]}")
print(f"Columns : {df.shape[1]}")

print("\nColumn Names")
print("-" * 60)
for column in df.columns:
    print(column)

print("\nMissing Values")
print("-" * 60)
print(df.isnull().sum())

print("\nDataset Information")
print("-" * 60)
df.info()

print("\nFirst Five Records")
print("-" * 60)
print(df.head())

save_to_bronze(
    df,
    BRONZE_DIR
)


validate_dataset(df)


