"""Spark transformation logic for the Gold layer."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def _safe_col(df: DataFrame, *names: str):
    for n in names:
        if n in df.columns:
            return n
    return None


def daily_sales(df: DataFrame) -> DataFrame:
    # Derive purchase_date from the Silver timestamp to avoid relying on a pre-existing column.
    if "purchase_date" not in df.columns:
        df = df.withColumn(
            "purchase_date",
            F.to_date(F.col("order_purchase_timestamp")),
        )

    orders_col = _safe_col(df, "orders", "order_id")
    if orders_col is None:
        orders_col = "order_id"

    revenue_col = _safe_col(df, "revenue", "payment_value")
    if revenue_col is None:
        revenue_col = "revenue"

    return (
        df.groupBy("purchase_date")
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(revenue_col)).alias("revenue"),
        )
        .orderBy("purchase_date")
    )


def monthly_sales(df: DataFrame) -> DataFrame:
    # Derive month from the Silver timestamp to avoid relying on a pre-existing column.
    if "month" not in df.columns and "order_month" not in df.columns:
        df = df.withColumn(
            "month",
            F.date_format(F.col("order_purchase_timestamp"), "yyyy-MM"),
        )

    month_col = _safe_col(df, "month", "order_month")
    orders_col = _safe_col(df, "orders", "order_id")

    if month_col is None:
        month_col = "month"

    if orders_col is None:
        orders_col = "order_id"

    revenue_col = _safe_col(df, "revenue", "payment_value")
    if revenue_col is None:
        revenue_col = "revenue"

    return (
        df.groupBy(F.col(month_col).alias("month"))
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(revenue_col)).alias("revenue"),
        )
        .orderBy("month")
    )


def seller_performance(df: DataFrame) -> DataFrame:
    seller_id_col = _safe_col(df, "seller_id")
    orders_col = _safe_col(df, "orders", "order_id")
    revenue_col = _safe_col(df, "revenue", "payment_value")

    delivery_purchase_col = _safe_col(df, "order_purchase_timestamp")
    delivery_delivered_col = _safe_col(df, "order_delivered_customer_date")

    if seller_id_col is None:
        raise ValueError("Required column seller_id is missing")

    if orders_col is None:
        orders_col = "order_id"

    if revenue_col is None:
        revenue_col = "payment_value"

    delivery_days_expr = None
    if delivery_purchase_col and delivery_delivered_col:
        delivery_days_expr = (
            F.datediff(
                F.to_date(F.col(delivery_delivered_col)),
                F.to_date(F.col(delivery_purchase_col)),
            )
        )
    else:
        # If delivery timestamps are missing, avg_delivery_days will be null.
        delivery_days_expr = F.lit(None).cast("double")

    return (
        df.groupBy(F.col(seller_id_col).alias("seller_id"))
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(revenue_col)).alias("revenue"),
            F.avg(delivery_days_expr).alias("avg_delivery_days"),
        )
        .orderBy(F.col("revenue").desc())
    )


def payment_summary(df: DataFrame) -> DataFrame:
    payment_type_col = _safe_col(df, "payment_type")
    orders_col = _safe_col(df, "orders", "order_id")
    payment_value_col = _safe_col(df, "total_payment", "payment_value", "revenue")

    if payment_type_col is None:
        raise ValueError("Required column payment_type is missing")

    if orders_col is None:
        orders_col = "order_id"

    if payment_value_col is None:
        payment_value_col = "payment_value"

    return (
        df.groupBy(F.col(payment_type_col).alias("payment_type"))
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(payment_value_col)).alias("total_payment"),
            F.avg(F.col(payment_value_col)).alias("average_payment"),
        )
        .orderBy(F.col("total_payment").desc())
    )


def delivery_summary(df: DataFrame) -> DataFrame:
    delivered_col = _safe_col(df, "order_delivered_customer_date")
    purchase_col = _safe_col(df, "order_purchase_timestamp")
    if delivered_col is None or purchase_col is None:
        raise ValueError(
            "Delivery summary requires order_delivered_customer_date and order_purchase_timestamp"
        )

    delivery_days = F.datediff(F.to_date(F.col(delivered_col)), F.to_date(F.col(purchase_col)))

    # Task requests: delivery_status, avg_delivery_days.
    # Derive a simple status: delivered if delivered date not null, else not_delivered.
    delivery_status = F.when(F.col(delivered_col).isNotNull(), F.lit("delivered")).otherwise(
        F.lit("not_delivered")
    )

    return (
        df.withColumn("delivery_status", delivery_status)
        .groupBy("delivery_status")
        .agg(F.avg(delivery_days.cast("double")).alias("avg_delivery_days"))
        .orderBy(F.col("delivery_status"))
    )


def top_products(df: DataFrame) -> DataFrame:
    category_col = _safe_col(df, "product_category", "product_category_name")
    orders_col = _safe_col(df, "orders", "order_id")
    revenue_col = _safe_col(df, "revenue", "payment_value")

    if category_col is None:
        raise ValueError("Required product category column is missing")

    if orders_col is None:
        orders_col = "order_id"

    if revenue_col is None:
        revenue_col = "payment_value"

    return (
        df.groupBy(F.col(category_col).alias("product_category"))
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(revenue_col)).alias("revenue"),
        )
        .orderBy(F.col("revenue").desc())
    )


def top_states(df: DataFrame) -> DataFrame:
    state_col = _safe_col(df, "customer_state")
    orders_col = _safe_col(df, "orders", "order_id")
    revenue_col = _safe_col(df, "revenue", "payment_value")

    if state_col is None:
        raise ValueError("Required customer_state column is missing")

    if orders_col is None:
        orders_col = "order_id"

    if revenue_col is None:
        revenue_col = "payment_value"

    return (
        df.groupBy(F.col(state_col).alias("customer_state"))
        .agg(
            F.countDistinct(F.col(orders_col)).alias("orders"),
            F.sum(F.col(revenue_col)).alias("revenue"),
        )
        .orderBy(F.col("revenue").desc())
        
    )

