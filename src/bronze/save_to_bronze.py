from pathlib import Path
import pandas as pd

from src.utils.logger import logger


from src.config.settings import BRONZE_DIR


def save_to_bronze(df: pd.DataFrame, output_dir=BRONZE_DIR):
    """
    Save the raw dataframe into Bronze Layer.
    """

    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "bronze_orders.csv"

    df.to_csv(output_file, index=False)

    logger.info("Bronze Layer Created Successfully")
    logger.info(f"Saved Bronze Dataset -> {output_file}")

