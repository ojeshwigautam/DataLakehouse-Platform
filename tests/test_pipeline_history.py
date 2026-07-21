"""Tests for PipelineHistory."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.metadata.pipeline_history import PipelineHistory


@pytest.fixture
def history():
    """PipelineHistory with mocked database."""
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    with patch(
        "src.metadata.pipeline_history.get_database_engine",
        return_value=mock_engine,
    ):
        with patch(
            "src.metadata.pipeline_history.Session",
            return_value=mock_session,
        ):
            h = PipelineHistory()
            h._mock_engine = mock_engine
            h._mock_session = mock_session
            yield h


class TestPipelineHistoryRecordStart:
    """Tests for record_start."""

    def test_record_start_returns_run_id(self, history):
        """Should return a non-empty string run_id."""
        run_id = history.record_start()
        assert run_id is not None
        assert isinstance(run_id, str)
        assert len(run_id) == 36  # UUID4 length

    def test_record_start_adds_run_record(self, history):
        """Should add a PipelineRun with RUNNING status."""
        history.record_start()

        assert history._mock_session.add.called
        assert history._mock_session.commit.called

        added_run = history._mock_session.add.call_args[0][0]
        assert added_run.status == "RUNNING"


class TestPipelineHistoryRecordSuccess:
    """Tests for record_success."""

    def test_record_success_marks_success(self, history):
        """Should update status to SUCCESS with counts."""
        mock_run = MagicMock()
        mock_run.start_time = datetime.now()
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_run
        )

        result = history.record_success(
            run_id="test-run-id",
            rows_processed=5000,
            files_processed=10,
        )

        assert result is True
        assert mock_run.status == "SUCCESS"
        assert mock_run.rows_processed == 5000
        assert mock_run.files_processed == 10
        assert history._mock_session.commit.called

    def test_record_success_not_found(self, history):
        """Should return False if run not found."""
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = history.record_success(
            run_id="non-existent",
            rows_processed=0,
            files_processed=0,
        )
        assert result is False


class TestPipelineHistoryRecordFailure:
    """Tests for record_failure."""

    def test_record_failure_marks_failed(self, history):
        """Should update status to FAILED with error."""
        mock_run = MagicMock()
        mock_run.start_time = datetime.now()
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_run
        )

        result = history.record_failure(
            run_id="test-run-id",
            error_message="Something failed",
        )

        assert result is True
        assert mock_run.status == "FAILED"
        assert mock_run.error_message == "Something failed"
        assert history._mock_session.commit.called

    def test_record_failure_not_found(self, history):
        """Should return False if run not found."""
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = history.record_failure(
            run_id="non-existent",
            error_message="error",
        )
        assert result is False


class TestPipelineHistoryRecordDuration:
    """Tests for record_execution_duration."""

    def test_record_duration_explicit(self, history):
        """Should use explicit duration when provided."""
        mock_run = MagicMock()
        mock_run.start_time = datetime.now()
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_run
        )

        result = history.record_execution_duration(
            run_id="test-run-id",
            duration_seconds=120,
        )

        assert result is True
        assert mock_run.duration_seconds == 120
        assert history._mock_session.commit.called

    def test_record_duration_not_found(self, history):
        """Should return False if run not found."""
        history._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = history.record_execution_duration(
            run_id="non-existent",
            duration_seconds=60,
        )
        assert result is False
