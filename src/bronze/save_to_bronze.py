from pathlib import Path

import pandas as pd

from src.config.settings import BRONZE_DIR
from src.storage.file_handler import FileHandler
from src.utils.logger import logger


def save_to_bronze(df: pd.DataFrame, output_dir=BRONZE_DIR):
    """Save the raw dataframe into Bronze Layer."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "bronze_orders.parquet"

    FileHandler.write(df, output_file)

    logger.info("Bronze Layer Created Successfully")
    logger.info(f"Saved Bronze Dataset -> {output_file}")
