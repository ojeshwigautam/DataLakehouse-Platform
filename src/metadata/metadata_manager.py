"""
Central MetadataManager that orchestrates all metadata operations
for pipeline runs, processed files, watermarks, and stage metrics.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.settings import METADATA_SCHEMA
from src.database.connection import get_database_engine
from src.metadata.metadata_models import (
    Base,
    PipelineMetric,
    PipelineRun,
    ProcessedFile,
    Watermark,
)
from src.utils.logger import logger


class MetadataManager:
    """High-level interface for metadata CRUD operations."""

    def __init__(self):
        self.engine = get_database_engine()
        self.schema = METADATA_SCHEMA

    # ----------------------------------------------------------
    # Schema & Table Management
    # ----------------------------------------------------------

    def create_tables(self):
        """Create the metadata schema and all four tables if they
        do not already exist."""
        with self.engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
            logger.info(f"Schema '{self.schema}' verified / created")

        Base.metadata.create_all(self.engine)
        logger.info("All metadata tables verified / created")

    # ----------------------------------------------------------
    # Pipeline Runs
    # ----------------------------------------------------------

    def start_pipeline_run(
        self,
        pipeline_name: str = "Unified Commerce Lakehouse ETL",
    ) -> str:
        """Create a new pipeline run record and return its run_id."""
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
            f"Pipeline run started | run_id={run_id} | " f"pipeline={pipeline_name}"
        )
        return run_id

    def finish_pipeline_run(
        self,
        run_id: str,
        files_processed: int = 0,
        rows_processed: int = 0,
    ):
        """Mark a pipeline run as successfully completed."""
        now = datetime.now()

        with Session(self.engine) as session:
            run = session.query(PipelineRun).filter_by(run_id=run_id).first()
            if run is None:
                logger.error(f"Pipeline run not found: {run_id}")
                return False

            run.end_time = now
            run.status = "SUCCESS"
            run.duration_seconds = int((now - run.start_time).total_seconds())
            run.files_processed = files_processed
            run.rows_processed = rows_processed
            session.commit()

        logger.info(
            f"Pipeline run completed | run_id={run_id} | "
            f"duration={run.duration_seconds}s | "
            f"files={files_processed} | rows={rows_processed}"
        )
        return True

    def fail_pipeline_run(
        self,
        run_id: str,
        error_message: str,
    ):
        """Mark a pipeline run as failed with an error message."""
        now = datetime.now()

        with Session(self.engine) as session:
            run = session.query(PipelineRun).filter_by(run_id=run_id).first()
            if run is None:
                logger.error(f"Pipeline run not found: {run_id}")
                return False

            run.end_time = now
            run.status = "FAILED"
            run.duration_seconds = int((now - run.start_time).total_seconds())
            run.error_message = error_message
            session.commit()

        logger.info(
            f"Pipeline run failed | run_id={run_id} | "
            f"duration={run.duration_seconds}s | error={error_message}"
        )
        return True

    # ----------------------------------------------------------
    # Stage Metrics
    # ----------------------------------------------------------

    def log_stage(
        self,
        run_id: str,
        stage: str,
        rows_processed: int = 0,
        duration_seconds: float = 0.0,
        status: str = "SUCCESS",
    ):
        """Record a stage-level metric for a pipeline run."""
        with Session(self.engine) as session:
            metric = PipelineMetric(
                run_id=run_id,
                stage=stage,
                rows_processed=rows_processed,
                duration_seconds=duration_seconds,
                status=status,
            )
            session.add(metric)
            session.commit()

        logger.info(
            f"Stage logged | run_id={run_id} | "
            f"stage={stage} | rows={rows_processed} | "
            f"duration={duration_seconds}s | status={status}"
        )

    # ----------------------------------------------------------
    # Processed Files
    # ----------------------------------------------------------

    def get_processed_files(
        self,
        limit: int = 100,
    ) -> List[dict]:
        """Return the most recently processed files."""
        with Session(self.engine) as session:
            records = (
                session.query(ProcessedFile)
                .order_by(ProcessedFile.processed_timestamp.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "file_name": r.file_name,
                    "checksum": r.checksum,
                    "processed_timestamp": r.processed_timestamp.isoformat(),
                    "run_id": str(r.run_id),
                    "status": r.status,
                }
                for r in records
            ]

    def mark_file_processed(
        self,
        file_name: str,
        checksum: str,
        run_id: str,
        status: str = "SUCCESS",
    ):
        """Record a file as having been processed."""
        with Session(self.engine) as session:
            record = ProcessedFile(
                file_name=file_name,
                checksum=checksum,
                processed_timestamp=datetime.now(),
                run_id=run_id,
                status=status,
            )
            session.add(record)
            session.commit()

        logger.info(
            f"File marked processed | file={file_name} | "
            f"checksum={checksum[:16]}... | run_id={run_id}"
        )

    # ----------------------------------------------------------
    # Watermarks
    # ----------------------------------------------------------

    def get_watermark(
        self,
        pipeline_name: str,
    ) -> Optional[dict]:
        """Return the current watermark for a pipeline, or None."""
        with Session(self.engine) as session:
            wm = session.query(Watermark).filter_by(pipeline_name=pipeline_name).first()
            if wm is None:
                return None
            return {
                "pipeline_name": wm.pipeline_name,
                "last_processed_file": wm.last_processed_file,
                "last_processed_timestamp": (
                    wm.last_processed_timestamp.isoformat()
                    if wm.last_processed_timestamp
                    else None
                ),
                "updated_at": wm.updated_at.isoformat(),
            }

    def update_watermark(
        self,
        pipeline_name: str,
        last_processed_file: Optional[str] = None,
        last_processed_timestamp: Optional[datetime] = None,
    ):
        """Create or update a watermark for a pipeline."""
        now = datetime.now()

        with Session(self.engine) as session:
            wm = session.query(Watermark).filter_by(pipeline_name=pipeline_name).first()

            if wm is None:
                wm = Watermark(
                    pipeline_name=pipeline_name,
                    last_processed_file=last_processed_file,
                    last_processed_timestamp=(last_processed_timestamp or now),
                    updated_at=now,
                )
                session.add(wm)
            else:
                if last_processed_file is not None:
                    wm.last_processed_file = last_processed_file
                if last_processed_timestamp is not None:
                    wm.last_processed_timestamp = last_processed_timestamp
                wm.updated_at = now

            session.commit()

        logger.info(
            f"Watermark updated | pipeline={pipeline_name} | "
            f"file={last_processed_file} | "
            f"timestamp={last_processed_timestamp or now}"
        )
