import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import BRONZE_DATASET

from src.spark.readers import read_parquet


df = read_parquet(BRONZE_DATASET)

df.printSchema()

print(df.count())

