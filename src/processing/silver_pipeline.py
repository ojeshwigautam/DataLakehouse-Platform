from pathlib import Path
import pandas as pd


from src.config.settings import (
    BRONZE_DATASET,
    BRONZE_INCREMENTAL_DIR,
    SILVER_DIR,
)
from src.utils.logger import logger


def load_bronze_data():
    """
    Load historical Bronze data and merge available
    incremental Bronze batches.
    """

    logger.info("Loading Historical Bronze Dataset")

    historical_df = pd.read_csv(BRONZE_DATASET)

    logger.info(
        f"Historical Bronze Rows : {len(historical_df)}"
    )

    dataframes = [historical_df]

    # Find all incremental Bronze CSV files
    incremental_files = sorted(
        BRONZE_INCREMENTAL_DIR.glob("*.csv")
    )

    logger.info(
        f"Incremental Bronze Files Found : "
        f"{len(incremental_files)}"
    )

    for file_path in incremental_files:

        logger.info(
            f"Loading Incremental Bronze -> "
            f"{file_path.name}"
        )

        incremental_df = pd.read_csv(file_path)

        logger.info(
            f"Incremental Rows Loaded : {len(incremental_df)}"
        )

        dataframes.append(incremental_df)

    # Combine historical and incremental datasets
    combined_df = pd.concat(
        dataframes,
        ignore_index=True,
    )

    logger.info(
        f"Combined Bronze Rows : {len(combined_df)}"
    )

    return combined_df



def create_silver_layer():
    logger.info("=" * 60)
    logger.info("Creating Silver Layer")
    logger.info("=" * 60)

    # -------------------------------------------------
    # Load Historical + Incremental Bronze Data
    # -------------------------------------------------

    df = load_bronze_data()

    rows_before = len(df)


    # -------------------------------------------------
    # Remove Duplicate Records
    # -------------------------------------------------

    if "order_unique_id" in df.columns:

        logger.info(
            "Deduplicating using order_unique_id"
        )

        df = df.drop_duplicates(
            subset=["order_unique_id"],
            keep="last",
        )

    else:

        logger.warning(
            "order_unique_id not found. "
            "Using full-row deduplication."
        )

        df = df.drop_duplicates()

    duplicates_removed = (
        rows_before - len(df)
    )


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

    SILVER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        SILVER_DIR
        / "silver_orders.csv"
    )

    df.to_csv(
        str(output_path),
        index=False,
    )

    rows_after = len(df)

    logger.info(
        f"Rows Before Cleaning : {rows_before}"
    )

    logger.info(
        f"Rows After Cleaning  : {rows_after}"
    )

    logger.info(
        f"Duplicates Removed   : {duplicates_removed}"
    )

    logger.info(
        f"Silver Dataset Saved : {output_path}"
    )


    logger.info("Silver Layer Created Successfully")


if __name__ == "__main__":
    create_silver_layer()

