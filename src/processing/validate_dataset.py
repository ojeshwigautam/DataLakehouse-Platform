import pandas as pd

from src.utils.logger import logger


def validate_dataset(df: pd.DataFrame):
    """Validate dataset quality before processing."""

    logger.info("=" * 60)
    logger.info("DATA VALIDATION REPORT")
    logger.info("=" * 60)

    logger.info(f"Rows : {len(df)}")
    logger.info(f"Columns : {len(df.columns)}")

    duplicate_rows = df.duplicated().sum()
    logger.info(f"Duplicate Rows : {duplicate_rows}")

    missing_values = df.isnull().sum().sum()
    logger.info(f"Missing Values : {missing_values}")

    logger.info("Data Types")
    logger.info("-" * 60)
    logger.info(df.dtypes)

    logger.info("Validation Completed Successfully")

