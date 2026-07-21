import os
import pandas as pd
import pandera as pa
from pandera import Check

from src.validation.validation_utils import save_validation_report
from src.storage.file_handler import FileHandler
from src.config.settings import (
    GOLD_DIR,
    GOLD_DAILY_SALES,
    GOLD_MONTHLY_SALES,
    GOLD_PAYMENT_SUMMARY,
    GOLD_SELLER_PERFORMANCE,
    GOLD_TOP_PRODUCTS,
    GOLD_TOP_STATES,
    GOLD_DELIVERY_SUMMARY,
)


def validate_daily_sales():
    df = FileHandler.read(GOLD_DAILY_SALES)

    schema = pa.DataFrameSchema({
        "order_date": pa.Column(str, nullable=False),
        "total_orders": pa.Column(int, Check.ge(0)),
        "total_revenue": pa.Column(float, Check.ge(0)),
        "average_order_value": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_monthly_sales():
    df = FileHandler.read(GOLD_MONTHLY_SALES)

    schema = pa.DataFrameSchema({
        "order_month": pa.Column(str, nullable=False),
        "total_orders": pa.Column(int, Check.ge(0)),
        "total_revenue": pa.Column(float, Check.ge(0)),
        "average_order_value": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_payment_summary():
    df = FileHandler.read(GOLD_PAYMENT_SUMMARY)

    schema = pa.DataFrameSchema({
        "payment_type": pa.Column(str, nullable=False),
        "total_transactions": pa.Column(int, Check.ge(0)),
        "total_amount": pa.Column(float, Check.ge(0)),
        "average_payment": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_seller_performance():
    df = FileHandler.read(GOLD_SELLER_PERFORMANCE)

    schema = pa.DataFrameSchema({
        "seller_id": pa.Column(str, nullable=False),
        "total_orders": pa.Column(int, Check.ge(0)),
        "total_revenue": pa.Column(float, Check.ge(0)),
        "average_order_value": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_top_products():
    df = FileHandler.read(GOLD_TOP_PRODUCTS)

    schema = pa.DataFrameSchema({
        "product_category_name": pa.Column(str, nullable=False),
        "total_orders": pa.Column(int, Check.ge(0)),
        "total_revenue": pa.Column(float, Check.ge(0)),
        "average_price": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_top_states():
    df = FileHandler.read(GOLD_TOP_STATES)

    schema = pa.DataFrameSchema({
        "customer_state": pa.Column(str, nullable=False),
        "total_orders": pa.Column(int, Check.ge(0)),
        "total_revenue": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_delivery_summary():
    df = FileHandler.read(GOLD_DELIVERY_SUMMARY)

    schema = pa.DataFrameSchema({
        "average_delivery_days": pa.Column(float, Check.ge(0)),
        "minimum_delivery_days": pa.Column(float, Check.ge(0)),
        "maximum_delivery_days": pa.Column(float, Check.ge(0))
    }, strict=True, coerce=True)

    schema.validate(df)


def validate_gold():

    try:
        validate_daily_sales()
        print("✅ daily_sales")

        validate_monthly_sales()
        print("✅ monthly_sales")

        validate_payment_summary()
        print("✅ payment_summary")

        validate_seller_performance()
        print("✅ seller_performance")

        validate_top_products()
        print("✅ top_products")

        validate_top_states()
        print("✅ top_states")

        validate_delivery_summary()
        print("✅ delivery_summary")

        save_validation_report(
            "gold",
            True,
            "All Gold datasets validated successfully."
        )

        print("\n🎉 All Gold datasets validated successfully!")

    except Exception as e:

        save_validation_report(
            "gold",
            False,
            str(e)
        )

        raise


if __name__ == "__main__":
    validate_gold()

