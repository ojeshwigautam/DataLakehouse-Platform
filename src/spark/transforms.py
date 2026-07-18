"""Spark transformation logic for the Lakehouse."""

from __future__ import annotations

from pyspark.sql.functions import col, lower, trim, to_timestamp, upper
from pyspark.sql import DataFrame


def clean_orders(df: DataFrame) -> DataFrame:
    """Apply Silver-layer cleaning/standardization for orders."""

    if "order_unique_id" in df.columns:
        df = df.dropDuplicates(["order_unique_id"])
    else:
        df = df.dropDuplicates()

    # Clean text columns (trim)
    string_columns = [
        field.name
        for field in df.schema.fields
        if field.dataType.simpleString() == "string"
    ]

    for column in string_columns:
        df = df.withColumn(column, trim(col(column)))

    # Standardize city/state
    if "customer_city" in df.columns:
        df = df.withColumn("customer_city", lower(col("customer_city")))
    if "seller_city" in df.columns:
        df = df.withColumn("seller_city", lower(col("seller_city")))

    if "customer_state" in df.columns:
        df = df.withColumn("customer_state", upper(col("customer_state")))
    if "seller_state" in df.columns:
        df = df.withColumn("seller_state", upper(col("seller_state")))

    # Convert timestamp columns
    timestamp_columns = [
        "shipping_limit_date",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:
        if column in df.columns:
            df = df.withColumn(column, to_timestamp(col(column)))

    # Remove invalid numeric values
    for column in ["price", "payment_value", "freight_value"]:
        if column in df.columns:
            df = df.filter(col(column) >= 0)

    return df


