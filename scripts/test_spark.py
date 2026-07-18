import os
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when running as a script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.spark.session import get_spark

spark = get_spark()


print("=" * 50)
print(spark.version)
print("=" * 50)

spark.stop()

