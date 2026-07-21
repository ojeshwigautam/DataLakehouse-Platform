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
from src.ingestion.incremental_ingestion import process_incremental_files
from src.bronze.save_to_bronze import save_to_bronze
from src.processing.validate_dataset import validate_dataset
from src.processing.data_quality import run_data_quality_checks
from src.processing.silver_pipeline import create_silver_layer
from src.gold.gold_pipeline import create_gold_layer

from src.database.load_gold_tables import load_gold_tables
from src.database.validate_tables import validate_postgresql_tables
from src.database.pipeline_audit import (
    start_pipeline_audit,
    complete_pipeline_audit,
    fail_pipeline_audit,
)

from src.validation.bronze_validation import validate_bronze
from src.validation.silver_validation import validate_silver
from src.validation.gold_validation import validate_gold


# ------------------------------------------------------------------
# Stage 1 — Bronze
# ------------------------------------------------------------------
def run_bronze():
    """STEP 2/9 : Load raw data and save to the Bronze layer.

    This stage is self-contained — it reads its own input from disk
    and writes its output to disk.  No DataFrame is passed in, making
    it suitable for Airflow tasks where retries must be independent.
    """
    logger.info("STEP 2/9 : Bronze Layer")

    df = load_dataset(RAW_DATASET)

    save_to_bronze(df)

    logger.info("Bronze Layer Completed")


# ------------------------------------------------------------------
# Stage 2 — Bronze Validation
# ------------------------------------------------------------------
def run_bronze_validation():
    """STEP 3/8 : Validate Bronze layer data."""
    logger.info("STEP 3/8 : Bronze Validation")
    validate_bronze(BRONZE_DATASET)
    logger.info("Bronze Validation Completed")


# ------------------------------------------------------------------
# Stage 3 — Silver
# ------------------------------------------------------------------
def run_silver():
    """STEP 4/8 : Create Silver layer from Bronze."""
    logger.info("STEP 4/8 : Silver Layer")
    create_silver_layer()
    logger.info("Silver Layer Completed")


# ------------------------------------------------------------------
# Stage 4 — Silver Validation
# ------------------------------------------------------------------
def run_silver_validation():
    """STEP 5/8 : Validate Silver layer data."""
    logger.info("STEP 5/8 : Silver Validation")
    validate_silver(SILVER_DATASET)
    logger.info("Silver Validation Completed")


# ------------------------------------------------------------------
# Stage 5 — Gold
# ------------------------------------------------------------------
def run_gold():
    """STEP 6/8 : Create Gold layer from Silver."""
    logger.info("STEP 6/8 : Gold Layer")
    create_gold_layer()
    logger.info("Gold Layer Completed")


# ------------------------------------------------------------------
# Stage 6 — Gold Validation
# ------------------------------------------------------------------
def run_gold_validation():
    """STEP 7/8 : Validate Gold layer datasets."""
    logger.info("STEP 7/8 : Gold Validation")
    validate_gold()
    logger.info("Gold Validation Completed")


# ------------------------------------------------------------------
# Stage 7 — PostgreSQL Load
# ------------------------------------------------------------------
def run_postgres():
    """STEP 8/8 : Load Gold tables into PostgreSQL."""
    logger.info("STEP 8/8 : PostgreSQL")
    tables = load_gold_tables()
    logger.info("PostgreSQL Load Completed")
    return tables


# ------------------------------------------------------------------
# Stage 8 — PostgreSQL Validation
# ------------------------------------------------------------------
def run_postgres_validation():
    """STEP 9/9 : Validate PostgreSQL tables."""
    logger.info("STEP 9/9 : PostgreSQL Validation")
    if not validate_postgresql_tables():
        raise RuntimeError("PostgreSQL validation failed.")
    logger.info("PostgreSQL Validation Completed")


# ------------------------------------------------------------------
# Stage — Data Quality
# ------------------------------------------------------------------
def run_data_quality():
    """Run legacy data quality checks on the loaded dataset.

    This stage is self-contained — it reads its own input from disk.
    """
    logger.info("Data Quality Checks")

    df = load_dataset(RAW_DATASET)

    validate_dataset(df)
    run_data_quality_checks(df)
    logger.info("Data Quality Checks Completed")


# ==================================================================
# Main Pipeline Orchestrator
# ==================================================================
def run_pipeline():
    """Execute the complete ETL pipeline."""

    start_time = datetime.now()
    run_id = None
    incremental_files = []

    logger.info("=" * 70)
    logger.info("UNIFIED COMMERCE LAKEHOUSE ETL PIPELINE")
    logger.info(f"Started : {start_time}")
    logger.info("=" * 70)

    try:
        run_id = start_pipeline_audit()

        logger.info("=" * 70)
        logger.info("UNIFIED COMMERCE LAKEHOUSE ETL PIPELINE")
        logger.info(f"Run ID  : {run_id}")
        logger.info(f"Started : {start_time}")
        logger.info("=" * 70)

        # -------------------------------------------------
        # STEP 1 — Bronze Layer (loads dataset internally)
        # -------------------------------------------------
        run_bronze()

        # -------------------------------------------------
        # STEP 2 — Bronze Validation
        # -------------------------------------------------
        run_bronze_validation()

        # -------------------------------------------------
        # Silver Layer
        # -------------------------------------------------
        run_silver()

        # -------------------------------------------------
        # Silver Validation
        # -------------------------------------------------
        run_silver_validation()

        # -------------------------------------------------
        # Gold Layer
        # -------------------------------------------------
        run_gold()

        # -------------------------------------------------
        # Gold Validation
        # -------------------------------------------------
        run_gold_validation()

        # -------------------------------------------------
        # PostgreSQL Load
        # -------------------------------------------------
        loaded_tables = run_postgres()

        # -------------------------------------------------
        # PostgreSQL Validation
        # -------------------------------------------------
        run_postgres_validation()

        # -------------------------------------------------
        # Incremental Data Ingestion (legacy)
        # -------------------------------------------------
        logger.info("Incremental Data Ingestion")
        incremental_files = process_incremental_files()
        logger.info(f"Incremental batches processed : {len(incremental_files)}")

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------
        end_time = datetime.now()
        execution_time = end_time - start_time

        gold_files = list(GOLD_DIR.glob("*.parquet"))

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
        logger.info("Incremental Processing")
        logger.info("-" * 70)
        logger.info(f"Incremental Batches Processed : {len(incremental_files)}")

        for file_path in incremental_files:
            logger.info(f"[OK] {file_path.name}")

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

        complete_pipeline_audit(
            run_id=run_id,
            start_time=start_time,
            incremental_batches=len(incremental_files),
        )

        return True

    except Exception as error:
        logger.error("=" * 70)
        logger.error("PIPELINE FAILED")
        logger.error(error)
        logger.error(traceback.format_exc())
        logger.error("=" * 70)

        if run_id is not None:
            try:
                fail_pipeline_audit(
                    run_id=run_id,
                    start_time=start_time,
                    error_message=str(error),
                )
            except Exception as audit_error:
                logger.error(
                    f"Failed to update pipeline audit: {audit_error}"
                )

        return False

