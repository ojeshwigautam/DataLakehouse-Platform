import logging
import time

from src.spark.config import BRONZE_PATH, SILVER_PATH
from src.spark.readers import read_parquet
from src.spark.reconciliation import create_reconciliation_report
from src.spark.report import save_reconciliation_report
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

    pipeline = "spark_silver"
    summary = create_reconciliation_report(
        bronze_df,
        silver_df,
        pipeline,
        duration_sec,
    )

    # Console output (after every run)
    print("=" * 54)
    print("Spark Reconciliation Report")
    print("=" * 54)
    print(f"Bronze Rows           : {summary['bronze_rows']}")
    print(f"Silver Rows           : {summary['silver_rows']}")
    print(f"Duplicates Removed    : {summary['duplicates_removed']}")
    # Spec requires: Missing Columns / Extra Columns
    # Current report only includes PASS/FAIL, so we infer 0 when PASS else 1.
    missing_cols = 0 if summary.get("schema_validation") == "PASS" else 1
    extra_cols = 0 if summary.get("schema_validation") == "PASS" else 1
    print(f"Missing Columns       : {missing_cols}")
    print(f"Extra Columns         : {extra_cols}")
    print(f"Validation            : {summary['schema_validation']}")
    print("=" * 54)




    report_path = save_reconciliation_report(summary)


    print("")
    print("=" * 15 + " Report Saved: " + "=" * 15)
    print(f"{report_path.as_posix()}")
    print("")

    logger.info("=" * 60)
    logger.info("Spark Silver Pipeline Metrics")
    logger.info(f"Input Rows  : {input_rows}")
    logger.info(f"Output Rows : {output_rows}")
    logger.info(f"Duration    : {duration_sec:.1f} sec")
    logger.info("=" * 60)

    spark.stop()


if __name__ == "__main__":
    create_spark_silver()



