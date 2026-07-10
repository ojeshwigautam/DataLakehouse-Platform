from datetime import datetime
import traceback

from src.config.settings import RAW_DATASET
from src.utils.logger import logger

from src.ingestion.load_dataset import load_dataset
from src.bronze.save_to_bronze import save_to_bronze
from src.processing.validate_dataset import validate_dataset
from src.processing.silver_pipeline import create_silver_layer


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
        logger.info("STEP 1/4 : Loading Dataset")

        df = load_dataset(RAW_DATASET)

        logger.info("Step 1 Completed")

        # -------------------------------------------------
        # Step 2 - Bronze
        # -------------------------------------------------
        logger.info("STEP 2/4 : Bronze Layer")

        save_to_bronze(df)

        logger.info("Step 2 Completed")

        # -------------------------------------------------
        # Step 3 - Validation
        # -------------------------------------------------
        logger.info("STEP 3/4 : Validation")


        validate_dataset(df)

        logger.info("Step 3 Completed")

        # -------------------------------------------------
        # Step 4 - Silver
        # -------------------------------------------------
        logger.info("STEP 4/4 : Silver Layer")

        create_silver_layer()

        logger.info("Step 4 Completed")

        end_time = datetime.now()

        logger.info("=" * 70)
        logger.info("PIPELINE EXECUTED SUCCESSFULLY")
        logger.info(f"Execution Time : {end_time - start_time}")
        logger.info("=" * 70)

        return True

    except Exception as error:
        logger.error("=" * 70)
        logger.error("PIPELINE FAILED")
        logger.error(error)
        logger.error(traceback.format_exc())
        logger.error("=" * 70)
        return False

