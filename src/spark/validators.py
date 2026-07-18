"""Spark DataFrame validation helpers."""

from __future__ import annotations

from typing import Iterable

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DecimalType,
    DoubleType,
    FloatType,
)


class ValidationError(ValueError):
    pass




def _required_columns_exist(df: DataFrame, required_columns: Iterable[str]) -> list[str]:
    df_cols = set(df.columns)
    missing = [c for c in required_columns if c not in df_cols]
    return missing


def validate_silver_orders(df: DataFrame) -> None:
    """Validate the Silver-layer DataFrame before writing."""

    if df is None:
        raise ValidationError("Silver validation failed: DataFrame is None")

    input_count = df.count()
    if input_count <= 0:
        raise ValidationError("Silver validation failed: Row count must be > 0")

    # Columns we expect based on transformations
    required = [
        "order_unique_id",
        "customer_city",
        "customer_state",
        "seller_city",
        "seller_state",
        "shipping_limit_date",
        "order_purchase_timestamp",
        "price",
        "payment_value",
        "freight_value",
    ]

    missing = _required_columns_exist(df, required)
    if missing:
        raise ValidationError(
            "Silver validation failed: Missing required columns: "
            + ", ".join(missing)
        )

    # No duplicate order_unique_id
    dup_count = (
        df.groupBy("order_unique_id")
        .count()
        .filter(F.col("count") > 1)
        .count()
    )

    if dup_count > 0:
        raise ValidationError(
            f"Silver validation failed: Found {dup_count} duplicate order_unique_id values"
        )

    # Critical columns not entirely null
    critical = [
        "order_unique_id",
        "order_purchase_timestamp",
        "price",
        "payment_value",
        "freight_value",
    ]


    def count_missing(df: DataFrame, field) -> int:
        column = field.name
        if isinstance(field.dataType, (DoubleType, FloatType, DecimalType)):
            return df.filter(
                F.col(column).isNull() | F.isnan(F.col(column))
            ).count()

        return df.filter(F.col(column).isNull()).count()

    for field in df.schema.fields:
        if field.name not in critical:
            continue

        missing = count_missing(df, field)
        if missing >= input_count:
            raise ValidationError(
                f"Silver validation failed: Column '{field.name}' is entirely null"
            )



