"""
Tests for the PipelineMonitor module.

Test scenarios:
    - Pipeline status is recorded.
    - Monitor retrieves pipeline summary.
    - Monitor retrieves latest run.
    - Monitor retrieves stage metrics.
    - Monitor produces dashboard data.
"""

from unittest.mock import MagicMock, patch

from src.monitoring.pipeline_monitor import PipelineMonitor, get_pipeline_monitor


class TestPipelineMonitor:
    """Tests for the PipelineMonitor class."""

    @patch("src.monitoring.pipeline_monitor.get_database_engine")
    def test_get_pipeline_summary(self, mock_get_engine):
        """Monitor should retrieve pipeline summary with correct statistics."""
        # Mock the database connection and result
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.first.return_value = {
            "total_runs": 10,
            "successful_runs": 8,
            "failed_runs": 2,
            "avg_duration_seconds": 42.5,
            "total_incremental_batches": 5,
        }
        mock_conn.execute.return_value.mappings.return_value = mock_result

        summary = PipelineMonitor.get_pipeline_summary()

        assert summary["total_runs"] == 10
        assert summary["successful_runs"] == 8
        assert summary["failed_runs"] == 2
        assert summary["success_rate"] == 80.0  # 8/10 * 100
        assert summary["avg_duration_seconds"] == 42.5
        assert summary["total_incremental_batches"] == 5

    @patch("src.monitoring.pipeline_monitor.get_database_engine")
    def test_get_pipeline_summary_empty(self, mock_get_engine):
        """Monitor should return zeros when no runs exist."""
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.first.return_value = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_duration_seconds": None,
            "total_incremental_batches": 0,
        }
        mock_conn.execute.return_value.mappings.return_value = mock_result

        summary = PipelineMonitor.get_pipeline_summary()

        assert summary["total_runs"] == 0
        assert summary["success_rate"] == 0.0

    @patch("src.monitoring.pipeline_monitor.get_database_engine")
    def test_get_latest_run(self, mock_get_engine):
        """Monitor should retrieve the latest pipeline run."""
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        expected = {
            "run_id": "abc-123",
            "pipeline_name": "Test Pipeline",
            "start_time": "2026-07-22 10:00:00",
            "end_time": "2026-07-22 10:15:00",
            "status": "SUCCESS",
            "execution_time_seconds": 900.0,
            "incremental_batches": 3,
            "error_message": None,
        }
        mock_result.first.return_value = expected
        mock_conn.execute.return_value.mappings.return_value = mock_result

        latest = PipelineMonitor.get_latest_run()

        assert latest is not None
        assert latest["run_id"] == "abc-123"
        assert latest["status"] == "SUCCESS"
        assert latest["execution_time_seconds"] == 900.0

    @patch("src.monitoring.pipeline_monitor.get_database_engine")
    def test_get_latest_run_empty(self, mock_get_engine):
        """Monitor should return None when no runs exist."""
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_conn.execute.return_value.mappings.return_value = mock_result

        latest = PipelineMonitor.get_latest_run()
        assert latest is None

    @patch("src.monitoring.pipeline_monitor.get_database_engine")
    def test_get_stage_metrics(self, mock_get_engine):
        """Monitor should retrieve stage metrics for a run."""
        mock_conn = MagicMock()
        mock_engine = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_result = MagicMock()
        mock_result.all.return_value = [
            {
                "run_id": "abc-123",
                "stage": "Bronze ETL",
                "duration_seconds": 15.0,
                "rows_processed": 113390,
                "status": "SUCCESS",
                "timestamp": "2026-07-22 10:00:00",
            },
            {
                "run_id": "abc-123",
                "stage": "Silver ETL",
                "duration_seconds": 25.0,
                "rows_processed": 100000,
                "status": "SUCCESS",
                "timestamp": "2026-07-22 10:05:00",
            },
        ]
        mock_conn.execute.return_value.mappings.return_value = mock_result

        metrics = PipelineMonitor.get_stage_metrics("abc-123")

        assert len(metrics) == 2
        assert metrics[0]["stage"] == "Bronze ETL"
        assert metrics[1]["stage"] == "Silver ETL"

    @patch("src.monitoring.pipeline_monitor.PipelineMonitor.get_pipeline_summary")
    @patch("src.monitoring.pipeline_monitor.PipelineMonitor.get_latest_run")
    @patch("src.monitoring.pipeline_monitor.PipelineMonitor.get_stage_metrics")
    def test_get_monitoring_dashboard_data(self, mock_stage, mock_latest, mock_summary):
        """Monitor should produce complete dashboard data."""
        mock_summary.return_value = {
            "total_runs": 10,
            "successful_runs": 8,
            "failed_runs": 2,
            "success_rate": 80.0,
            "avg_duration_seconds": 42.5,
            "total_incremental_batches": 5,
        }
        mock_latest.return_value = {
            "run_id": "abc-123",
            "pipeline_name": "Test Pipeline",
            "status": "SUCCESS",
        }
        mock_stage.return_value = [
            {"stage": "Bronze ETL", "duration_seconds": 15.0},
        ]

        data = PipelineMonitor.get_monitoring_dashboard_data()

        assert "summary" in data
        assert "latest_run" in data
        assert "stage_metrics" in data
        assert "generated_at" in data
        assert data["summary"]["total_runs"] == 10
        assert data["latest_run"]["run_id"] == "abc-123"

    def test_get_pipeline_monitor_factory(self):
        """Factory function should return a PipelineMonitor instance."""
        monitor = get_pipeline_monitor()
        assert isinstance(monitor, PipelineMonitor)
