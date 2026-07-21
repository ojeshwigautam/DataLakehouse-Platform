"""
Structured pipeline stage logger for monitoring pipeline execution.

Provides per-component loggers that write to individual log files:
    - pipeline.log   : Main pipeline orchestration
    - bronze.log     : Bronze layer operations
    - silver.log     : Silver layer operations
    - gold.log       : Gold layer operations
    - postgres.log   : PostgreSQL operations
    - airflow.log    : Airflow DAG operations

Also provides a StageLogger class for structured stage-level logging.
"""

import logging
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from src.config.settings import LOG_DIR

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ── Per-component log file mapping ─────────────────────────────────

LOG_FILES: Dict[str, Path] = {
    "pipeline": LOG_DIR / "pipeline.log",
    "bronze": LOG_DIR / "bronze.log",
    "silver": LOG_DIR / "silver.log",
    "gold": LOG_DIR / "gold.log",
    "postgres": LOG_DIR / "postgres.log",
    "airflow": LOG_DIR / "airflow.log",
}


# ── Ensure all log directories exist ──────────────────────────────

LOG_DIR.mkdir(parents=True, exist_ok=True)
for log_path in LOG_FILES.values():
    log_path.parent.mkdir(parents=True, exist_ok=True)


# ── Logger Registry (cached loggers) ──────────────────────────────

_loggers: Dict[str, logging.Logger] = {}


def get_logger(component: str = "pipeline") -> logging.Logger:
    """Get a per-component logger that writes to its own log file.

    Parameters
    ----------
    component : str
        One of 'pipeline', 'bronze', 'silver', 'gold', 'postgres', 'airflow'.

    Returns
    -------
    logging.Logger
        Logger instance configured for the specified component.
    """
    if component in _loggers:
        return _loggers[component]

    logger = logging.getLogger(f"DataLakehouse.{component}")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.handlers:
        _loggers[component] = logger
        return logger

    # ── File handler (component-specific) ─────────────────────
    log_file = LOG_FILES.get(component, LOG_DIR / f"{component}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # ── Stream handler (console) ──────────────────────────────
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    _loggers[component] = logger
    return logger


# ── Aliases for common components ─────────────────────────────────

pipeline_logger = get_logger("pipeline")
bronze_logger = get_logger("bronze")
silver_logger = get_logger("silver")
gold_logger = get_logger("gold")
postgres_logger = get_logger("postgres")
airflow_logger = get_logger("airflow")


# ── Stage Logger (structured stage-level logging) ─────────────────


class StageLogger:
    """Logger for individual pipeline stages with timing and context.

    Extends the concept of get_logger with a specific stage name,
    providing structured start/end/error logging.

    Usage::

        stage_logger = StageLogger("Bronze ETL")
        stage_logger.log_start()
        # perform work
        stage_logger.log_rows_processed(113390)
        stage_logger.log_end()
    """

    def __init__(self, stage_name: str, component: str = "pipeline"):
        self.stage_name = stage_name
        self._logger = get_logger(component)
        self._start_time: Optional[float] = None

    # ── Logging methods ───────────────────────────────────────

    def log_start(self):
        """Log that a pipeline stage has started."""
        self._start_time = time.time()
        self._logger.info(
            f"[{self.stage_name}] START | " f"timestamp={datetime.now().isoformat()}"
        )

    def log_end(self):
        """Log that a pipeline stage has ended."""
        if self._start_time is None:
            self._logger.warning(
                f"[{self.stage_name}] log_end called without log_start"
            )
            return
        duration = time.time() - self._start_time
        self._logger.info(
            f"[{self.stage_name}] END | "
            f"duration={duration:.2f}s | "
            f"timestamp={datetime.now().isoformat()}"
        )

    def log_duration(self, duration_seconds: float):
        """Log the duration of a completed stage."""
        self._logger.info(
            f"[{self.stage_name}] DURATION | " f"duration={duration_seconds:.2f}s"
        )

    def log_rows_processed(self, row_count: int):
        """Log the number of rows processed by this stage."""
        self._logger.info(f"[{self.stage_name}] ROWS | " f"rows_processed={row_count}")

    def log_info(self, message: str):
        """Log an informational message for this stage."""
        self._logger.info(f"[{self.stage_name}] {message}")

    def log_warning(self, message: str):
        """Log a warning message for this stage."""
        self._logger.warning(f"[{self.stage_name}] {message}")

    def log_error(self, error_message: str):
        """Log an error that occurred in this stage."""
        self._logger.error(f"[{self.stage_name}] ERROR | " f"message={error_message}")

    def log_critical(self, error_message: str):
        """Log a critical error for this stage."""
        self._logger.critical(
            f"[{self.stage_name}] CRITICAL | " f"message={error_message}"
        )

    def log_exception(self, error_message: str):
        """Log an exception with traceback."""
        self._logger.exception(
            f"[{self.stage_name}] EXCEPTION | " f"message={error_message}"
        )

    # ── Context manager for automatic timing ──────────────────

    @contextmanager
    def track_stage(self):
        """Context manager that logs start, end, and duration.

        Usage::

            logger = StageLogger("bronze")
            with logger.track_stage():
                # perform stage work
                pass
        """
        self.log_start()
        try:
            yield
        except Exception as exc:
            self.log_error(str(exc))
            raise
        finally:
            self.log_end()


def get_stage_logger(stage_name: str, component: str = "pipeline") -> StageLogger:
    """Factory function to create a StageLogger for a given stage."""
    return StageLogger(stage_name, component)
