import pytest
from pyspark.sql import Row
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

from src.spark.validators import ValidationError, validate_silver_orders


def test_validate_silver_orders_passes(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city="new york",
            customer_state="NY",
            seller_city="los angeles",
            seller_state="CA",
            shipping_limit_date="2026-01-05 10:00:00",
            order_purchase_timestamp="2026-01-01 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        ),
        Row(
            order_unique_id="o2",
            customer_city="sf",
            customer_state="CA",
            seller_city="seattle",
            seller_state="WA",
            shipping_limit_date="2026-01-06 11:00:00",
            order_purchase_timestamp="2026-01-02 11:00:00",
            price=200.0,
            payment_value=210.0,
            freight_value=20.0,
        ),
    ]

    df = spark.createDataFrame(data)

    # Should not raise
    validate_silver_orders(df)


def test_validate_silver_orders_fails_on_duplicate_order_unique_id(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city="new york",
            customer_state="NY",
            seller_city="los angeles",
            seller_state="CA",
            shipping_limit_date="2026-01-05 10:00:00",
            order_purchase_timestamp="2026-01-01 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        ),
        Row(
            order_unique_id="o1",
            customer_city="new york",
            customer_state="NY",
            seller_city="los angeles",
            seller_state="CA",
            shipping_limit_date="2026-01-05 10:00:00",
            order_purchase_timestamp="2026-01-01 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        ),
    ]

    df = spark.createDataFrame(data)

    with pytest.raises(ValidationError, match="duplicate order_unique_id"):
        validate_silver_orders(df)


def test_validate_silver_orders_fails_on_missing_required_columns(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city="new york",
            customer_state="NY",
            # missing seller_city
            seller_state="CA",
            shipping_limit_date="2026-01-05 10:00:00",
            order_purchase_timestamp="2026-01-01 10:00:00",
            price=100.0,
            payment_value=110.0,
            freight_value=10.0,
        )
    ]

    df = spark.createDataFrame(data)

    with pytest.raises(ValidationError, match="Missing required columns"):
        validate_silver_orders(df)


def test_validate_silver_orders_fails_on_all_null_critical_column(spark):
    data = [
        Row(
            order_unique_id="o1",
            customer_city="new york",
            customer_state="NY",
            seller_city="los angeles",
            seller_state="CA",
            shipping_limit_date="2026-01-05 10:00:00",
            order_purchase_timestamp="2026-01-01 10:00:00",
            price=None,
            payment_value=110.0,
            freight_value=10.0,
        ),
        Row(
            order_unique_id="o2",
            customer_city="sf",
            customer_state="CA",
            seller_city="seattle",
            seller_state="WA",
            shipping_limit_date="2026-01-06 11:00:00",
            order_purchase_timestamp="2026-01-02 11:00:00",
            price=None,
            payment_value=210.0,
            freight_value=20.0,
        ),
    ]

    schema = StructType(
        [
            StructField("order_unique_id", StringType(), False),
            StructField("customer_city", StringType(), True),
            StructField("customer_state", StringType(), True),
            StructField("seller_city", StringType(), True),
            StructField("seller_state", StringType(), True),
            StructField("shipping_limit_date", StringType(), True),
            StructField("order_purchase_timestamp", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("payment_value", DoubleType(), True),
            StructField("freight_value", DoubleType(), True),
        ]
    )

    df = spark.createDataFrame(data, schema=schema)

    with pytest.raises(ValidationError, match="price.*entirely null"):
        validate_silver_orders(df)
