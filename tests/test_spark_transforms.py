from pyspark.sql import Row

from src.spark.transforms import clean_orders


def test_clean_orders_drops_duplicates_and_cleans_fields(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city=" New York ",
            seller_city="Los  Angeles",
            customer_state="ny",
            seller_state="ca",
            order_purchase_timestamp="2026-01-01 10:00:00",
            shipping_limit_date="2026-01-05 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        ),
        # duplicate order_unique_id should be removed
        Row(
            order_unique_id="o1",
            customer_city=" New York ",
            seller_city="Los  Angeles",
            customer_state="ny",
            seller_state="ca",
            order_purchase_timestamp="2026-01-01 10:00:00",
            shipping_limit_date="2026-01-05 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        ),
        Row(
            order_unique_id="o2",
            customer_city="  san francisco",
            seller_city="Seattle  ",
            customer_state="ca",
            seller_state="wa",
            order_purchase_timestamp="2026-01-02 11:00:00",
            shipping_limit_date="2026-01-06 11:00:00",
            price=200.0,
            payment_value=210.0,
            freight_value=20.0,
        ),
    ]

    df = spark.createDataFrame(data)

    cleaned = clean_orders(df)

    assert cleaned.count() == 2

    row = cleaned.filter(cleaned.order_unique_id == "o1").collect()[0]
    assert row.customer_city == "new york"
    assert row.seller_city == "los  angeles"  # trim + lower, internal spaces preserved
    assert row.customer_state == "NY"
    assert row.seller_state == "CA"


def test_clean_orders_filters_negative_numeric_values_and_converts_timestamps(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city="a",
            seller_city="b",
            customer_state="x",
            seller_state="y",
            order_purchase_timestamp="2026-01-01 10:00:00",
            shipping_limit_date="2026-01-05 10:00:00",
            price=-1.0,
            payment_value=10.0,
            freight_value=1.0,
        ),
        Row(
            order_unique_id="o2",
            customer_city="a",
            seller_city="b",
            customer_state="x",
            seller_state="y",
            order_purchase_timestamp="2026-01-02 11:00:00",
            shipping_limit_date="2026-01-06 11:00:00",
            price=2.0,
            payment_value=-3.0,
            freight_value=1.0,
        ),
        Row(
            order_unique_id="o3",
            customer_city="a",
            seller_city="b",
            customer_state="x",
            seller_state="y",
            order_purchase_timestamp="2026-01-03 12:00:00",
            shipping_limit_date="2026-01-07 12:00:00",
            price=2.0,
            payment_value=3.0,
            freight_value=-1.0,
        ),
        Row(
            order_unique_id="o4",
            customer_city="a",
            seller_city="b",
            customer_state="x",
            seller_state="y",
            order_purchase_timestamp="2026-01-04 12:00:00",
            shipping_limit_date="2026-01-08 12:00:00",
            price=2.0,
            payment_value=3.0,
            freight_value=1.0,
        ),
    ]

    df = spark.createDataFrame(data)
    cleaned = clean_orders(df)

    assert cleaned.count() == 1
    assert cleaned.collect()[0].order_unique_id == "o4"

    # sanity: conversion produced non-null timestamps for at least one row
    assert cleaned.filter(cleaned.order_purchase_timestamp.isNotNull()).count() == 1

