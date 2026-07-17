from datetime import datetime
import traceback

from src.config.settings import (
    RAW_DATASET,
    BRONZE_DATASET,
    SILVER_DATASET,
    GOLD_DIR,
)

from src.utils.logger import logger

from src.ingestion.load_dataset import load_dataset
from src.bronze.save_to_bronze import save_to_bronze
from src.processing.validate_dataset import validate_dataset
from src.processing.silver_pipeline import create_silver_layer
from src.gold.gold_pipeline import create_gold_layer
from src.database.load_gold_tables import load_gold_tables
from src.database.validate_tables import validate_postgresql_tables








def run_pipeline():
    """Execute the complete ETL pipeline."""


    start_time = datetime.now()

    logger.info("=" * 70)
    logger.info("UNIFIED COMMERCE LAKEHOUSE ETL PIPELINE")
    logger.info(f"Started : {start_time}")
    logger.info("=" * 70)

    try:
        # -------------------------------------------------
        # Step 1 - Load
        # -------------------------------------------------
        logger.info("STEP 1/7 : Loading Dataset")



        df = load_dataset(RAW_DATASET)

        logger.info("Step 1 Completed")

        # -------------------------------------------------
        # Step 2 - Bronze
        # -------------------------------------------------
        logger.info("STEP 2/7 : Bronze Layer")



        save_to_bronze(df)

        logger.info("Step 2 Completed")

        # -------------------------------------------------
        # Step 3 - Validation
        # -------------------------------------------------
        logger.info("STEP 3/7 : Data Validation")





        validate_dataset(df)

        logger.info("Step 3 Completed")

        # -------------------------------------------------
        # Step 4 - Silver
        # -------------------------------------------------

        logger.info("STEP 4/7 : Silver Layer")


        create_silver_layer()

        logger.info("Step 4 Completed")


        # -------------------------------------------------
        # Step 5 - Gold
        # -------------------------------------------------

        logger.info("STEP 5/7 : Gold Layer")


        create_gold_layer()
        logger.info("Step 5 Completed")


        logger.info("STEP 6/7 : PostgreSQL Loading")

        loaded_tables = load_gold_tables()
        logger.info("Step 6 Completed")

        logger.info("STEP 7/7 : PostgreSQL Validation")

        database_valid = validate_postgresql_tables()

        if not database_valid:
            raise RuntimeError(
                "PostgreSQL database validation failed"
            )

        logger.info("Step 7 Completed")


        end_time = datetime.now()
        execution_time = end_time - start_time

        # Count generated Gold datasets
        gold_files = list(GOLD_DIR.glob("*.csv"))

        logger.info("=" * 70)
        logger.info("PIPELINE EXECUTED SUCCESSFULLY")
        logger.info("=" * 70)

        logger.info("")
        logger.info("PIPELINE SUMMARY")
        logger.info("-" * 70)

        logger.info(f"Raw Dataset        : {RAW_DATASET.name}")
        logger.info(f"Bronze Dataset     : {BRONZE_DATASET.name}")
        logger.info(f"Silver Dataset     : {SILVER_DATASET.name}")

        logger.info("")
        logger.info(f"Gold Datasets Generated : {len(gold_files)}")

        for file in gold_files:
            logger.info(f"[OK] {file.name}")

        logger.info("")
        logger.info(f"PostgreSQL Tables Loaded : {len(loaded_tables)}")

        for table in loaded_tables:
            logger.info(f"[OK] {table}")

        logger.info("")
        logger.info(f"Execution Time     : {execution_time}")
        logger.info("Pipeline Status    : SUCCESS")


        logger.info("=" * 70)

        return True


    except Exception as error:
        logger.error("=" * 70)
        logger.error("PIPELINE FAILED")
        logger.error(error)
        logger.error(traceback.format_exc())
        logger.error("=" * 70)
        return False

