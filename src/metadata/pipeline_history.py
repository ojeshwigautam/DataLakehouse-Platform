"""
PipelineHistory — Record every pipeline execution with success/failure
status, duration, and row counts.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.database.connection import get_database_engine
from src.metadata.metadata_models import PipelineRun
from src.utils.logger import logger


class PipelineHistory:
    """Record and query pipeline execution history."""

    def __init__(self):
        self.engine = get_database_engine()

    # ----------------------------------------------------------
    # Record Start
    # ----------------------------------------------------------

    def record_start(
        self,
        pipeline_name: str = "Unified Commerce Lakehouse ETL",
    ) -> str:
        """Record the start of a pipeline execution.

        Returns the run_id (UUID string) for the new execution.
        """
        import uuid

        run_id = str(uuid.uuid4())
        now = datetime.now()

        with Session(self.engine) as session:
            run = PipelineRun(
                run_id=run_id,
                start_time=now,
                status="RUNNING",
            )
            session.add(run)
            session.commit()

        logger.info(
            f"Pipeline execution started | run_id={run_id} | "
            f"pipeline={pipeline_name}"
        )
        return run_id

    # ----------------------------------------------------------
    # Record Success
    # ----------------------------------------------------------

    def record_success(
        self,
        run_id: str,
        rows_processed: int = 0,
        files_processed: int = 0,
    ):
        """Mark a pipeline execution as successfully completed.

        Automatically computes execution duration.
        """
        now = datetime.now()

        with Session(self.engine) as session:
            run = session.query(PipelineRun).filter_by(run_id=run_id).first()
            if run is None:
                logger.error(f"Cannot record success — run not found: {run_id}")
                return False

            run.end_time = now
            run.status = "SUCCESS"
            run.duration_seconds = int((now - run.start_time).total_seconds())
            run.rows_processed = rows_processed
            run.files_processed = files_processed
            session.commit()

        logger.info(
            f"Pipeline execution succeeded | run_id={run_id} | "
            f"duration={run.duration_seconds}s | "
            f"rows={rows_processed} | files={files_processed}"
        )
        return True

    # ----------------------------------------------------------
    # Record Failure
    # ----------------------------------------------------------

    def record_failure(
        self,
        run_id: str,
        error_message: str,
    ):
        """Mark a pipeline execution as failed."""
        now = datetime.now()

        with Session(self.engine) as session:
            run = session.query(PipelineRun).filter_by(run_id=run_id).first()
            if run is None:
                logger.error(f"Cannot record failure — run not found: {run_id}")
                return False

            run.end_time = now
            run.status = "FAILED"
            run.duration_seconds = int((now - run.start_time).total_seconds())
            run.error_message = error_message
            session.commit()

        logger.info(
            f"Pipeline execution failed | run_id={run_id} | "
            f"duration={run.duration_seconds}s | "
            f"error={error_message}"
        )
        return True

    # ----------------------------------------------------------
    # Record Duration (explicit)
    # ----------------------------------------------------------

    def record_execution_duration(
        self,
        run_id: str,
        duration_seconds: Optional[int] = None,
    ):
        """Update the execution duration for a pipeline run.

        If duration_seconds is not provided, it is computed from
        start_time to now.
        """
        now = datetime.now()

        with Session(self.engine) as session:
            run = session.query(PipelineRun).filter_by(run_id=run_id).first()
            if run is None:
                logger.error(f"Cannot record duration — run not found: {run_id}")
                return False

            if duration_seconds is None:
                duration_seconds = int((now - run.start_time).total_seconds())

            run.duration_seconds = duration_seconds
            session.commit()

        logger.info(
            f"Execution duration recorded | run_id={run_id} | "
            f"duration={duration_seconds}s"
        )
        return True
