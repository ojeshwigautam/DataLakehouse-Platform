import uuid
from datetime import datetime

from sqlalchemy import text

from src.database.connection import get_database_engine
from src.utils.logger import logger


def create_audit_table():
    """Create the pipeline audit table if it does not already exist."""

    engine = get_database_engine()

    query = text(
        """
        CREATE TABLE IF NOT EXISTS pipeline_audit (
            run_id VARCHAR(36) PRIMARY KEY,
            pipeline_name VARCHAR(100) NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            status VARCHAR(20) NOT NULL,
            execution_time_seconds FLOAT,
            incremental_batches INTEGER DEFAULT 0,
            error_message TEXT
        )
        """
    )

    with engine.begin() as connection:
        connection.execute(query)

    logger.info("Pipeline audit table verified")


def start_pipeline_audit():
    """Create a new audit record when the pipeline starts."""

    create_audit_table()

    run_id = str(uuid.uuid4())

    engine = get_database_engine()

    query = text(
        """
        INSERT INTO pipeline_audit (
            run_id,
            pipeline_name,
            start_time,
            status
        )
        VALUES (
            :run_id,
            :pipeline_name,
            :start_time,
            :status
        )
        """
    )

    parameters = {
        "run_id": run_id,
        "pipeline_name": "Unified Commerce Lakehouse ETL",
        "start_time": datetime.now(),
        "status": "RUNNING",
    }

    with engine.begin() as connection:
        connection.execute(query, parameters)

    logger.info(f"Pipeline audit started | Run ID : {run_id}")

    return run_id


def complete_pipeline_audit(
    run_id,
    start_time,
    incremental_batches=0,
):
    """Mark a pipeline execution as successfully completed."""

    end_time = datetime.now()

    execution_time = (end_time - start_time).total_seconds()

    engine = get_database_engine()

    query = text(
        """
        UPDATE pipeline_audit
        SET
            end_time = :end_time,
            status = :status,
            execution_time_seconds = :execution_time,
            incremental_batches = :incremental_batches
        WHERE run_id = :run_id
        """
    )

    parameters = {
        "run_id": run_id,
        "end_time": end_time,
        "status": "SUCCESS",
        "execution_time": execution_time,
        "incremental_batches": incremental_batches,
    }

    with engine.begin() as connection:
        connection.execute(query, parameters)

    logger.info(f"Pipeline audit completed | Run ID : {run_id}")


def fail_pipeline_audit(
    run_id,
    start_time,
    error_message,
):
    """Mark a pipeline execution as failed."""

    end_time = datetime.now()

    execution_time = (end_time - start_time).total_seconds()

    engine = get_database_engine()

    query = text(
        """
        UPDATE pipeline_audit
        SET
            end_time = :end_time,
            status = :status,
            execution_time_seconds = :execution_time,
            error_message = :error_message
        WHERE run_id = :run_id
        """
    )

    parameters = {
        "run_id": run_id,
        "end_time": end_time,
        "status": "FAILED",
        "execution_time": execution_time,
        "error_message": str(error_message),
    }

    with engine.begin() as connection:
        connection.execute(query, parameters)

    logger.info(f"Pipeline audit failed | Run ID : {run_id}")
