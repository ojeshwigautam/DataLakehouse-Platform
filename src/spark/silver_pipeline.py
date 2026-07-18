import logging
import time

from src.spark.config import BRONZE_PATH, SILVER_PATH
from src.spark.readers import read_parquet
from src.spark.session import get_spark
from src.spark.transforms import clean_orders
from src.spark.validators import validate_silver_orders
from src.spark.writers import write_parquet

logger = logging.getLogger(__name__)


def create_spark_silver() -> None:
    logging.basicConfig(level=logging.INFO)

    spark = get_spark()
    start_time = time.perf_counter()

    logger.info("=" * 60)
    logger.info("Reading Bronze layer...")

    bronze_df = read_parquet(BRONZE_PATH)
    input_rows = bronze_df.count()

    logger.info("Cleaning records (Silver transformations)...")
    silver_df = clean_orders(bronze_df)

    logger.info("Validating Silver dataset...")
    validate_silver_orders(silver_df)

    output_rows = silver_df.count()

    logger.info("Writing Silver layer...")
    write_parquet(silver_df, SILVER_PATH)

    duration_sec = time.perf_counter() - start_time

    logger.info("=" * 60)
    logger.info("Spark Silver Pipeline Metrics")
    logger.info(f"Input Rows  : {input_rows}")
    logger.info(f"Output Rows : {output_rows}")
    logger.info(f"Duration    : {duration_sec:.1f} sec")
    logger.info("=" * 60)

    spark.stop()


if __name__ == "__main__":
    create_spark_silver()


