"""
Tests for the monitoring logger module.

Test scenarios:
    - Logger creates log files.
    - Logger writes messages at different levels.
    - StageLogger logs start/end/duration/rows/errors.
    - Component-specific loggers write to correct files.
"""

import pytest

from src.monitoring.logger import (
    LOG_DIR,
    LOG_FILES,
    StageLogger,
    get_logger,
    get_stage_logger,
)


class TestGetLogger:
    """Tests for the get_logger function."""

    def test_logger_creates_log_file(self):
        """Logger should create the corresponding log file on first use."""
        component = "test_pipeline"
        logger = get_logger(component)
        logger.info("Test log message")

        # Check that the log file was created
        log_file = LOG_FILES.get(component, LOG_DIR / f"{component}.log")
        assert log_file.exists(), f"Log file {log_file} should exist"

    def test_logger_levels(self):
        """Logger should correctly log at INFO, WARNING, ERROR, CRITICAL levels."""
        component = "test_levels"
        logger = get_logger(component)

        # These should not raise any exceptions
        logger.info("INFO test message")
        logger.warning("WARNING test message")
        logger.error("ERROR test message")
        logger.critical("CRITICAL test message")

        log_file = LOG_FILES.get(component, LOG_DIR / f"{component}.log")
        content = log_file.read_text(encoding="utf-8")

        assert "INFO" in content
        assert "WARNING" in content
        assert "ERROR" in content
        assert "CRITICAL" in content

    def test_logger_reuses_instance(self):
        """get_logger should return the same instance for the same component."""
        logger1 = get_logger("test_reuse")
        logger2 = get_logger("test_reuse")
        assert logger1 is logger2, "Logger instances should be cached and reused"

    def test_component_loggers_different_files(self):
        """Different components should write to different log files."""
        comp1_logger = get_logger("test_comp1")
        comp2_logger = get_logger("test_comp2")

        comp1_logger.info("Component 1 message")
        comp2_logger.info("Component 2 message")

        log1 = LOG_FILES.get("test_comp1", LOG_DIR / "test_comp1.log")
        log2 = LOG_FILES.get("test_comp2", LOG_DIR / "test_comp2.log")

        content1 = log1.read_text(encoding="utf-8")
        content2 = log2.read_text(encoding="utf-8")

        assert "Component 1 message" in content1
        assert "Component 2 message" in content2


class TestStageLogger:
    """Tests for the StageLogger class."""

    def test_log_start_end(self):
        """StageLogger should log start and end events."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_start()
        stage_logger.log_end()

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] START" in content
        assert "[test_stage] END" in content

    def test_log_rows_processed(self):
        """StageLogger should log rows processed count."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_rows_processed(5000)

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] ROWS" in content
        assert "rows_processed=5000" in content

    def test_log_error(self):
        """StageLogger should log error messages."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_error("Something went wrong")

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] ERROR" in content
        assert "Something went wrong" in content

    def test_log_critical(self):
        """StageLogger should log critical messages."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_critical("Critical failure")

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] CRITICAL" in content
        assert "Critical failure" in content

    def test_log_duration(self):
        """StageLogger should log duration."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_duration(42.5)

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] DURATION" in content
        assert "duration=42.50s" in content

    def test_log_info_warning(self):
        """StageLogger should log info and warning messages."""
        stage_logger = StageLogger("test_stage", "test_pipeline")
        stage_logger.log_info("Processing started")
        stage_logger.log_warning("Memory usage high")

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_stage] Processing started" in content
        assert "[test_stage] Memory usage high" in content

    def test_track_stage_context_manager(self):
        """track_stage context manager should log start and end."""
        stage_logger = StageLogger("test_context", "test_pipeline")

        with stage_logger.track_stage():
            pass  # Simulate stage work

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_context] START" in content
        assert "[test_context] END" in content

    def test_track_stage_with_exception(self):
        """track_stage should log error if exception occurs."""
        stage_logger = StageLogger("test_exc", "test_pipeline")

        with pytest.raises(ValueError):
            with stage_logger.track_stage():
                raise ValueError("Test error")

        log_file = LOG_FILES.get("test_pipeline", LOG_DIR / "test_pipeline.log")
        content = log_file.read_text(encoding="utf-8")

        assert "[test_exc] ERROR" in content
        assert "Test error" in content


class TestGetStageLogger:
    """Tests for the get_stage_logger factory function."""

    def test_factory_creates_stage_logger(self):
        """get_stage_logger should return a StageLogger instance."""
        stage_logger = get_stage_logger("factory_test", "test_pipeline")
        assert isinstance(stage_logger, StageLogger)
        assert stage_logger.stage_name == "factory_test"
