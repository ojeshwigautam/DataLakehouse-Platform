import pandas as pd
from pathlib import Path

# Dataset path
DATASET_PATH = Path("data/raw/historical/Brazilian E-Commerce Public Dataset by Olist.csv")

print("=" * 60)
print("UNIFIED COMMERCE LAKEHOUSE")
print("Dataset Inspection")
print("=" * 60)

# Read dataset
df = pd.read_csv(DATASET_PATH)

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
print(df.info())

print("\nFirst Five Records")
print("-" * 60)
print(df.head())

