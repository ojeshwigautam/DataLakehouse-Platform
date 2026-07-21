"""
Tests for the PipelineMetrics module.

Test scenarios:
    - Metrics are stored correctly.
    - Metrics record start/complete/fail.
    - Metrics work as context manager.
    - Metrics capture rows processed.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.monitoring.metrics import PipelineMetrics, create_pipeline_metrics


class TestPipelineMetrics:
    """Tests for the PipelineMetrics class."""

    def test_metrics_start_complete(self):
        """Metrics should record start and complete successfully."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            metrics = PipelineMetrics("test_stage", run_id="test-run-123")
            metrics.start()

            assert metrics.stage == "test_stage"
            assert metrics.run_id == "test-run-123"

            metrics.rows_processed = 5000
            result = metrics.complete()

            assert result["stage"] == "test_stage"
            assert result["rows_processed"] == 5000
            assert result["status"] == "SUCCESS"
            assert result["duration_seconds"] >= 0

    def test_metrics_fail(self):
        """Metrics should record a failure correctly."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            metrics = PipelineMetrics("test_stage", run_id="test-run-123")
            metrics.start()
            result = metrics.fail("Something went wrong")

            assert result["status"] == "FAILED"
            assert result["error_message"] == "Something went wrong"

    def test_metrics_context_manager_success(self):
        """Metrics context manager should complete successfully."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            with PipelineMetrics("ctx_test", run_id="test-run-456") as m:
                m.rows_processed = 1000

            # If we got here without exception, it worked
            assert m.status == "SUCCESS"

    def test_metrics_context_manager_failure(self):
        """Metrics context manager should fail on exception."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            with pytest.raises(RuntimeError):
                with PipelineMetrics("ctx_fail", run_id="test-run-789") as m:
                    m.rows_processed = 500
                    raise RuntimeError("Intentional failure")

            assert m.status == "FAILED"

    def test_metrics_rows_processed(self):
        """Metrics should track rows processed."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            metrics = PipelineMetrics("rows_test", run_id="test-run-rows")
            metrics.start()
            metrics.rows_processed = 113390
            result = metrics.complete()

            assert result["rows_processed"] == 113390

    def test_metrics_files_processed(self):
        """Metrics should track files processed."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            metrics = PipelineMetrics("files_test", run_id="test-files")
            metrics.start()
            metrics.files_processed = 5
            result = metrics.complete()

            assert result["files_processed"] == 5

    def test_metrics_duration_recorded(self):
        """Metrics should record a positive duration."""
        with patch("src.monitoring.metrics.get_database_engine") as mock_engine:
            mock_engine.return_value.begin.return_value.__enter__.return_value = (
                MagicMock()
            )

            metrics = PipelineMetrics("duration_test", run_id="test-dur")
            metrics.start()
            metrics.complete()

            assert metrics.duration_seconds >= 0

    def test_create_pipeline_metrics_factory(self):
        """Factory function should create a PipelineMetrics instance."""
        metrics = create_pipeline_metrics("factory_test")
        assert isinstance(metrics, PipelineMetrics)
        assert metrics.stage == "factory_test"
