"""Tests for MetadataManager."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.metadata.metadata_manager import MetadataManager


@pytest.fixture
def manager():
    """MetadataManager with all internal dependencies mocked."""
    mock_engine = MagicMock()
    mock_session = MagicMock()

    # Make the session context manager return itself
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    with patch(
        "src.metadata.metadata_manager.get_database_engine",
        return_value=mock_engine,
    ):
        with patch(
            "src.metadata.metadata_manager.Session",
            return_value=mock_session,
        ):
            mgr = MetadataManager()
            mgr._mock_engine = mock_engine
            mgr._mock_session = mock_session
            yield mgr


class TestMetadataManagerCreateTables:
    """Tests for create_tables."""

    def test_create_tables_creates_schema(self, manager):
        """Should execute CREATE SCHEMA IF NOT EXISTS."""
        mock_conn = MagicMock()
        mock_engine_begin = MagicMock()
        mock_engine_begin.__enter__.return_value = mock_conn
        mock_engine_begin.__exit__.return_value = None
        manager.engine.begin.return_value = mock_engine_begin

        manager.create_tables()
        assert mock_conn.execute.called

    def test_create_tables_creates_metadata(self, manager):
        """Should call metadata.create_all."""
        with patch(
            "src.metadata.metadata_manager.Base.metadata.create_all"
        ) as mock_create:
            manager.create_tables()
            mock_create.assert_called_once_with(manager.engine)


class TestMetadataManagerPipelineRuns:
    """Tests for pipeline run lifecycle."""

    def test_start_pipeline_run_returns_id(self, manager):
        """Should return a non-empty string run_id."""
        run_id = manager.start_pipeline_run()
        assert run_id is not None
        assert isinstance(run_id, str)
        assert len(run_id) == 36  # UUID length

    def test_finish_pipeline_run_updates_status(self, manager):
        """Should mark pipeline as SUCCESS."""
        mock_run = MagicMock()
        mock_run.start_time = datetime.now()
        mock_run.status = "RUNNING"

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_run
        )

        result = manager.finish_pipeline_run(
            run_id="test-run-id",
            files_processed=5,
            rows_processed=1000,
        )
        assert result is True
        assert mock_run.status == "SUCCESS"
        assert mock_run.files_processed == 5
        assert mock_run.rows_processed == 1000

    def test_finish_pipeline_run_not_found(self, manager):
        """Should return False if run not found."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = manager.finish_pipeline_run(run_id="non-existent-run-id")
        assert result is False

    def test_fail_pipeline_run_marks_failed(self, manager):
        """Should mark pipeline as FAILED with error."""
        mock_run = MagicMock()
        mock_run.start_time = datetime.now()

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_run
        )

        result = manager.fail_pipeline_run(
            run_id="test-run-id",
            error_message="Something went wrong",
        )
        assert result is True
        assert mock_run.status == "FAILED"
        assert mock_run.error_message == "Something went wrong"

    def test_fail_pipeline_run_not_found(self, manager):
        """Should return False if run not found."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = manager.fail_pipeline_run(
            run_id="non-existent-run-id",
            error_message="error",
        )
        assert result is False


class TestMetadataManagerStageMetrics:
    """Tests for stage metric logging."""

    def test_log_stage_adds_record(self, manager):
        """Should add a PipelineMetric record."""
        manager.log_stage(
            run_id="test-run-id",
            stage="bronze",
            rows_processed=500,
            duration_seconds=12.5,
            status="SUCCESS",
        )

        assert manager._mock_session.add.called
        assert manager._mock_session.commit.called

        added_metric = manager._mock_session.add.call_args[0][0]
        assert added_metric.stage == "bronze"
        assert added_metric.rows_processed == 500
        assert added_metric.duration_seconds == 12.5


class TestMetadataManagerProcessedFiles:
    """Tests for processed file tracking."""

    def test_mark_file_processed_adds_record(self, manager):
        """Should add a ProcessedFile record."""
        manager.mark_file_processed(
            file_name="test.csv",
            checksum="abc123",
            run_id="test-run-id",
            status="SUCCESS",
        )

        assert manager._mock_session.add.called
        assert manager._mock_session.commit.called

    def test_get_processed_files_returns_list(self, manager):
        """Should return a list of processed file dicts."""
        mock_record = MagicMock()
        mock_record.file_name = "test.csv"
        mock_record.checksum = "abc123"
        mock_record.processed_timestamp = datetime.now()
        mock_record.run_id = uuid.uuid4()
        mock_record.status = "SUCCESS"

        manager._mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_record
        ]

        result = manager.get_processed_files(limit=10)
        assert len(result) == 1
        assert result[0]["file_name"] == "test.csv"
        assert result[0]["status"] == "SUCCESS"


class TestMetadataManagerWatermarks:
    """Tests for watermark operations."""

    def test_get_watermark_returns_none_when_missing(self, manager):
        """Should return None for non-existent watermark."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = manager.get_watermark("test-pipeline")
        assert result is None

    def test_get_watermark_returns_dict(self, manager):
        """Should return watermark dict when found."""
        mock_wm = MagicMock()
        mock_wm.pipeline_name = "test-pipeline"
        mock_wm.last_processed_file = "last_file.csv"
        mock_wm.last_processed_timestamp = datetime(2026, 1, 1, 12, 0, 0)
        mock_wm.updated_at = datetime(2026, 1, 1, 12, 0, 0)

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_wm
        )

        result = manager.get_watermark("test-pipeline")
        assert result is not None
        assert result["pipeline_name"] == "test-pipeline"
        assert result["last_processed_file"] == "last_file.csv"

    def test_update_watermark_creates_new(self, manager):
        """Should create a new watermark if none exists."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        manager.update_watermark(
            pipeline_name="test-pipeline",
            last_processed_file="file.csv",
            last_processed_timestamp=datetime(2026, 1, 1),
        )

        assert manager._mock_session.add.called
        assert manager._mock_session.commit.called
