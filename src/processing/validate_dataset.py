import pandas as pd

from src.monitoring.logger import get_logger

logger = get_logger("pipeline")


def validate_dataset(df: pd.DataFrame):
    """
    Validate dataset quality before processing.
    """

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
    for col_name, col_dtype in df.dtypes.items():
        logger.info(f"  {col_name:<30} {col_dtype}")

    logger.info("Validation Completed Successfully")
