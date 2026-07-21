"""
Pipeline Metrics — Capture and store per-stage execution metrics.

Records metrics in the ``metadata.pipeline_metrics`` table (PostgreSQL)
for every pipeline stage execution, including:
    - Stage name (Bronze / Silver / Gold / Validation / PostgreSQL)
    - Duration in seconds
    - Rows processed
    - Status (SUCCESS / FAILED)
    - Execution timestamp

Uses the existing :class:`src.metadata.metadata_models.PipelineMetric` ORM model.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import text

from src.database.connection import get_database_engine
from src.monitoring.execution_timer import ExecutionTimer
from src.monitoring.logger import get_logger

logger = get_logger("pipeline")


# ── Metrics Manager ───────────────────────────────────────────────


class PipelineMetrics:
    """Capture and store per-stage execution metrics.

    Usage::

        metrics = PipelineMetrics("Bronze ETL", run_id="abc-123")
        metrics.start()
        # perform stage work
        metrics.rows_processed = 113390
        metrics.complete()

    Or as a context manager::

        with PipelineMetrics("Bronze ETL", run_id="abc-123") as m:
            # perform stage work
            m.rows_processed = 113390
    """

    def __init__(
        self,
        stage: str,
        run_id: Optional[str] = None,
    ):
        self.stage = stage
        self.run_id = run_id
        self.rows_processed: int = 0
        self.files_processed: int = 0
        self._timer = ExecutionTimer(stage)
        self._status: str = "RUNNING"
        self._error_message: Optional[str] = None

    # ── Properties ────────────────────────────────────────────

    @property
    def duration_seconds(self) -> float:
        return self._timer.duration

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str):
        self._status = value.upper()

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, value: str):
        self._error_message = value
        self._status = "FAILED"

    # ── Public API ────────────────────────────────────────────

    def start(self) -> "PipelineMetrics":
        """Start recording metrics for this stage."""
        self._timer.start()
        logger.info(f"[{self.stage}] Metrics recording STARTED")
        return self

    def complete(self) -> Dict[str, Any]:
        """Mark the stage as complete and store metrics.

        Returns the metrics dictionary.
        """
        self._timer.stop()

        if self._status == "RUNNING":
            self._status = "SUCCESS"

        metrics_data = self._get_metrics_data()

        # Try to store in PostgreSQL if we have a run_id
        if self.run_id:
            try:
                self._store_metrics(metrics_data)
                logger.info(
                    f"[{self.stage}] Metrics stored to database | "
                    f"duration={self.duration_seconds:.2f}s | "
                    f"rows={self.rows_processed} | "
                    f"status={self._status}"
                )
            except Exception as exc:
                logger.warning(f"[{self.stage}] Failed to store metrics: {exc}")

        logger.info(
            f"[{self.stage}] Metrics recording COMPLETED | "
            f"duration={self.duration_seconds:.2f}s | "
            f"rows={self.rows_processed} | "
            f"status={self._status}"
        )

        return metrics_data

    def fail(self, error_message: str) -> Dict[str, Any]:
        """Mark the stage as failed and store metrics.

        Parameters
        ----------
        error_message : str
            Description of the error.
        """
        self._error_message = error_message
        self._status = "FAILED"
        return self.complete()

    # ── Context Manager ───────────────────────────────────────

    def __enter__(self) -> "PipelineMetrics":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.fail(str(exc_val))
        else:
            self.complete()
        return False

    # ── Internal helpers ──────────────────────────────────────

    def _get_metrics_data(self) -> Dict[str, Any]:
        """Build the metrics data dictionary."""
        return {
            "run_id": self.run_id,
            "stage": self.stage,
            "duration_seconds": round(self.duration_seconds, 2),
            "rows_processed": self.rows_processed,
            "files_processed": self.files_processed,
            "status": self._status,
            "error_message": self._error_message,
            "timestamp": datetime.now(),
        }

    def _store_metrics(self, metrics_data: Dict[str, Any]):
        """Store metrics in the metadata.pipeline_metrics table."""
        engine = get_database_engine()

        # Ensure metadata schema and table exist
        self._ensure_metrics_table(engine)

        query = text(
            """
            INSERT INTO metadata.pipeline_metrics
                (run_id, stage, duration_seconds, rows_processed, status, timestamp)
            VALUES
                (:run_id, :stage, :duration_seconds, :rows_processed, :status, :timestamp)
            """
        )

        params = {
            "run_id": metrics_data["run_id"],
            "stage": metrics_data["stage"],
            "duration_seconds": metrics_data["duration_seconds"],
            "rows_processed": metrics_data["rows_processed"],
            "status": metrics_data["status"],
            "timestamp": metrics_data["timestamp"],
        }

        with engine.begin() as connection:
            connection.execute(query, params)

    def _ensure_metrics_table(self, engine):
        """Create the metadata.pipeline_metrics table if it doesn't exist."""
        create_schema = text("CREATE SCHEMA IF NOT EXISTS metadata;")
        create_table = text(
            """
            CREATE TABLE IF NOT EXISTS metadata.pipeline_metrics (
                id SERIAL PRIMARY KEY,
                run_id VARCHAR(36),
                stage VARCHAR(50) NOT NULL,
                duration_seconds FLOAT,
                rows_processed BIGINT DEFAULT 0,
                status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
                timestamp TIMESTAMP NOT NULL DEFAULT NOW()
            );
            """
        )
        with engine.begin() as connection:
            connection.execute(create_schema)
            connection.execute(create_table)


# ── Factory function ──────────────────────────────────────────────


def create_pipeline_metrics(
    stage: str, run_id: Optional[str] = None
) -> PipelineMetrics:
    """Factory function to create a PipelineMetrics instance."""
    return PipelineMetrics(stage, run_id)
