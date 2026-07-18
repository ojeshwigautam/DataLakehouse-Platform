"""Spark Gold Pipeline.

Creates 7 Gold datasets from the Silver layer.
"""

from __future__ import annotations

import time

from pyspark.sql import DataFrame

from src.spark.config import (
    SILVER_PATH,
    DAILY_SALES_PATH,
    MONTHLY_SALES_PATH,
    SELLER_PERFORMANCE_PATH,
    PAYMENT_SUMMARY_PATH,
    DELIVERY_SUMMARY_PATH,
    TOP_PRODUCTS_PATH,
    TOP_STATES_PATH,
)
from src.spark.readers import read_parquet
from src.spark.session import get_spark
from src.spark.writers import write_parquet
from src.spark.gold_transforms import (
    daily_sales,
    monthly_sales,
    seller_performance,
    payment_summary,
    delivery_summary,
    top_products,
    top_states,
)
from src.spark.gold_validators import validate_gold_dataset


def _validate(name: str, df: DataFrame, required_columns: list[str], dimension_columns: list[str] | None = None):
    validate_gold_dataset(
        df,
        required_columns=required_columns,
        dimension_columns=dimension_columns,
    )


def main() -> None:
    spark = get_spark()

    start_time = time.time()

    print("=" * 40)
    print("Spark Gold Pipeline")
    print("=" * 40)

    silver_df = read_parquet(SILVER_PATH)

    artifacts: list[tuple[str, str, DataFrame, list[str], list[str] | None]] = []

    daily = daily_sales(silver_df)
    artifacts.append(
        ("Daily Sales", str(DAILY_SALES_PATH), daily, ["purchase_date", "orders", "revenue"], ["purchase_date"])
    )

    monthly = monthly_sales(silver_df)
    artifacts.append(
        ("Monthly Sales", str(MONTHLY_SALES_PATH), monthly, ["month", "orders", "revenue"], ["month"])
    )

    seller_perf = seller_performance(silver_df)
    artifacts.append(
        (
            "Seller Performance",
            str(SELLER_PERFORMANCE_PATH),
            seller_perf,
            ["seller_id", "orders", "revenue", "avg_delivery_days"],
            ["seller_id"],
        )
    )

    pay_sum = payment_summary(silver_df)
    artifacts.append(
        (
            "Payment Summary",
            str(PAYMENT_SUMMARY_PATH),
            pay_sum,
            ["payment_type", "orders", "total_payment", "average_payment"],
            ["payment_type"],
        )
    )

    del_sum = delivery_summary(silver_df)
    artifacts.append(
        (
            "Delivery Summary",
            str(DELIVERY_SUMMARY_PATH),
            del_sum,
            ["delivery_status", "avg_delivery_days"],
            ["delivery_status"],
        )
    )

    top_prod = top_products(silver_df)
    artifacts.append(
        (
            "Top Products",
            str(TOP_PRODUCTS_PATH),
            top_prod,
            ["product_category", "orders", "revenue"],
            ["product_category"],
        )
    )

    top_st = top_states(silver_df)
    artifacts.append(
        (
            "Top States",
            str(TOP_STATES_PATH),
            top_st,
            ["customer_state", "orders", "revenue"],
            ["customer_state"],
        )
    )

    rows_processed = 0
    created = 0

    for label, path, df, required_cols, dim_cols in artifacts:
        try:
            _validate(label, df, required_columns=required_cols, dimension_columns=dim_cols)
            rows_processed += df.count()
            write_parquet(df, path)
            created += 1
            print(f"{label:<20} PASS")
        except Exception as e:
            print(f"{label:<20} FAIL")
            raise

    exec_time = time.time() - start_time

    print("=" * 40)
    print(f"Gold Tables Created : {created}")
    print(f"Execution Time : {exec_time:.1f} sec")
    print(f"Rows Processed : {rows_processed}")
    print("=" * 40)


if __name__ == "__main__":
    main()

