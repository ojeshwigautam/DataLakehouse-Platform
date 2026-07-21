import pandas as pd

from src.utils.logger import logger

REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "seller_id",
    "price",
    "freight_value",
    "payment_value",
    "order_purchase_timestamp",
    "order_status",
]


def check_required_columns(df):
    """
    Verify that all required columns exist in the dataset.
    """

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    logger.info("[PASS] Required columns check")

    return True


def check_empty_dataset(df):
    """
    Verify that the dataset contains records.
    """

    if df.empty:
        raise ValueError("Dataset is empty")

    logger.info("[PASS] Empty dataset check")

    return True


def check_duplicate_rows(df):
    """
    Report duplicate rows in the dataset.
    """

    duplicate_count = df.duplicated().sum()

    logger.info(f"Duplicate rows detected : {duplicate_count}")

    logger.info("[PASS] Duplicate rows check")

    return True


def check_critical_nulls(df):
    """
    Verify that critical identifier columns do not contain null values.
    """

    critical_columns = [
        "order_id",
        "customer_id",
        "product_id",
        "seller_id",
    ]

    null_counts = df[critical_columns].isnull().sum()

    columns_with_nulls = null_counts[null_counts > 0].to_dict()

    if columns_with_nulls:
        raise ValueError(f"Critical null values detected: " f"{columns_with_nulls}")

    logger.info("[PASS] Critical null values check")

    return True


def check_numeric_values(df):
    """
    Verify that important monetary columns
    do not contain negative values.
    """

    numeric_columns = [
        "price",
        "freight_value",
        "payment_value",
    ]

    invalid_values = {}

    for column in numeric_columns:

        if column in df.columns:

            negative_count = (
                pd.to_numeric(
                    df[column],
                    errors="coerce",
                )
                < 0
            ).sum()

            if negative_count > 0:

                invalid_values[column] = int(negative_count)

    if invalid_values:
        raise ValueError(f"Negative numeric values detected: " f"{invalid_values}")

    logger.info("[PASS] Numeric value check")

    return True


def check_order_ids(df):
    """
    Verify that order IDs are present and valid.
    Multiple rows per order are allowed because
    an order may contain multiple items.
    """

    invalid_order_ids = df["order_id"].isnull().sum()

    if invalid_order_ids > 0:
        raise ValueError(f"Invalid order IDs detected: " f"{invalid_order_ids}")

    logger.info("[PASS] Order ID validation")

    return True


def check_timestamp_values(df):
    """
    Verify that order purchase timestamps
    can be converted to valid datetime values.
    """

    timestamps = pd.to_datetime(
        df["order_purchase_timestamp"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce",
    )

    invalid_timestamps = timestamps.isnull().sum()

    if invalid_timestamps > 0:
        raise ValueError(f"Invalid order purchase timestamps: " f"{invalid_timestamps}")

    logger.info("[PASS] Timestamp validation")

    return True


def run_data_quality_checks(df):
    """
    Execute all automated data quality checks.
    """

    logger.info("=" * 60)
    logger.info("AUTOMATED DATA QUALITY CHECKS")
    logger.info("=" * 60)

    checks = [
        check_empty_dataset,
        check_required_columns,
        check_duplicate_rows,
        check_critical_nulls,
        check_numeric_values,
        check_order_ids,
        check_timestamp_values,
    ]

    passed_checks = 0

    for check in checks:

        check(df)

        passed_checks += 1

    logger.info("-" * 60)
    logger.info(f"Data Quality Checks Passed : " f"{passed_checks}/{len(checks)}")
    logger.info("DATA QUALITY VALIDATION SUCCESSFUL")
    logger.info("=" * 60)

    return True
