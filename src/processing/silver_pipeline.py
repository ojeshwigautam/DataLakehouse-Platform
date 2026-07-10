from pathlib import Path
import pandas as pd

from src.config.settings import BRONZE_DATASET, SILVER_DIR
from src.utils.logger import logger


def create_silver_layer():
    logger.info("=" * 60)
    logger.info("Creating Silver Layer")
    logger.info("=" * 60)

    # Load Bronze dataset
    df = pd.read_csv(BRONZE_DATASET)

    rows_before = len(df)

    # -------------------------------------------------
    # Remove duplicate rows
    # -------------------------------------------------
    df = df.drop_duplicates()

    duplicates_removed = rows_before - len(df)

    # -------------------------------------------------
    # Clean text columns
    # -------------------------------------------------
    object_columns = df.select_dtypes(include="object").columns

    for column in object_columns:
        df[column] = df[column].astype(str).str.strip()

    # -------------------------------------------------
    # Standardize city names
    # -------------------------------------------------
    if "customer_city" in df.columns:
        df["customer_city"] = df["customer_city"].str.lower()

    if "seller_city" in df.columns:
        df["seller_city"] = df["seller_city"].str.lower()

    # -------------------------------------------------
    # Standardize state names
    # -------------------------------------------------
    if "customer_state" in df.columns:
        df["customer_state"] = df["customer_state"].str.upper()

    if "seller_state" in df.columns:
        df["seller_state"] = df["seller_state"].str.upper()

    # -------------------------------------------------
    # Convert timestamp columns
    # -------------------------------------------------
    date_columns = [
        "shipping_limit_date",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    # -------------------------------------------------
    # Remove invalid numeric values
    # -------------------------------------------------
    numeric_columns = [
        "price",
        "payment_value",
        "freight_value",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df = df[df[column] >= 0]

    # -------------------------------------------------
    # Save Silver dataset
    # -------------------------------------------------
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    output_path = SILVER_DIR / "silver_orders.csv"

    # Ensure directories exist and use an explicit string path for pandas
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    

    df.to_csv(str(output_path), index=False)



    logger.info(f"Rows Before Cleaning : {rows_before}")
    logger.info(f"Rows After Cleaning  : {len(df)}")
    logger.info(f"Duplicates Removed   : {duplicates_removed}")
    logger.info(f"Silver Dataset Saved : {output_path}")

    logger.info("Silver Layer Created Successfully")


if __name__ == "__main__":
    create_silver_layer()

