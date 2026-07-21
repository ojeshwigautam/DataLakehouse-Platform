import time
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/historical/olist_ecommerce_dataset.csv")
PARQUET = Path("data/bronze/historical/bronze_orders.parquet")


def benchmark_csv():

    start = time.perf_counter()

    df = pd.read_csv(RAW, low_memory=False)

    elapsed = time.perf_counter() - start

    return elapsed, df.memory_usage(deep=True).sum()


def benchmark_parquet():

    start = time.perf_counter()

    df = pd.read_parquet(PARQUET)

    elapsed = time.perf_counter() - start

    return elapsed, df.memory_usage(deep=True).sum()


csv_time, csv_mem = benchmark_csv()

parquet_time, parquet_mem = benchmark_parquet()

csv_size = RAW.stat().st_size
parquet_size = PARQUET.stat().st_size

print("=" * 60)
print(" STORAGE BENCHMARK ")
print("=" * 60)

print(f"CSV File Size       : {csv_size/1024/1024:.2f} MB")
print(f"Parquet File Size   : {parquet_size/1024/1024:.2f} MB")

print()

print(f"CSV Read Time       : {csv_time:.4f} sec")
print(f"Parquet Read Time   : {parquet_time:.4f} sec")

print()

print(f"CSV Memory Usage    : {csv_mem/1024/1024:.2f} MB")
print(f"Parquet Memory Usage: {parquet_mem/1024/1024:.2f} MB")
