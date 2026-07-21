"""Tests for WatermarkManager."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.metadata.watermark_manager import WatermarkManager


@pytest.fixture
def manager():
    """WatermarkManager with mocked database."""
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    with patch(
        "src.metadata.watermark_manager.get_database_engine",
        return_value=mock_engine,
    ):
        with patch(
            "src.metadata.watermark_manager.Session",
            return_value=mock_session,
        ):
            mgr = WatermarkManager()
            mgr._mock_engine = mock_engine
            mgr._mock_session = mock_session
            yield mgr


class TestWatermarkManagerGet:
    """Tests for get_watermark."""

    def test_get_watermark_returns_none_when_missing(self, manager):
        """Should return None when no watermark exists."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = manager.get_watermark("test-pipeline")
        assert result is None

    def test_get_watermark_returns_dict(self, manager):
        """Should return watermark dict with all expected keys."""
        mock_wm = MagicMock()
        mock_wm.pipeline_name = "test-pipeline"
        mock_wm.last_processed_file = "last_file.csv"
        mock_wm.last_processed_timestamp = datetime(2026, 6, 1, 10, 0, 0)
        mock_wm.updated_at = datetime(2026, 6, 1, 10, 30, 0)

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_wm
        )

        result = manager.get_watermark("test-pipeline")
        assert result is not None
        assert result["pipeline_name"] == "test-pipeline"
        assert result["last_processed_file"] == "last_file.csv"
        assert result["last_processed_timestamp"] == datetime(2026, 6, 1, 10, 0, 0)
        assert result["updated_at"] == datetime(2026, 6, 1, 10, 30, 0)


class TestWatermarkManagerUpdate:
    """Tests for update_watermark."""

    def test_update_watermark_creates_new(self, manager):
        """Should create a new Watermark record if none exists."""
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

    def test_update_watermark_updates_existing(self, manager):
        """Should update existing Watermark record."""
        mock_wm = MagicMock()
        mock_wm.last_processed_file = "old_file.csv"

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_wm
        )

        manager.update_watermark(
            pipeline_name="test-pipeline",
            last_processed_file="new_file.csv",
        )

        assert mock_wm.last_processed_file == "new_file.csv"
        assert manager._mock_session.commit.called


class TestWatermarkManagerReset:
    """Tests for reset_watermark."""

    def test_reset_watermark_clears_fields(self, manager):
        """Should set last_processed_file and timestamp to None."""
        mock_wm = MagicMock()
        mock_wm.last_processed_file = "file.csv"
        mock_wm.last_processed_timestamp = datetime.now()

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_wm
        )

        manager.reset_watermark("test-pipeline")

        assert mock_wm.last_processed_file is None
        assert mock_wm.last_processed_timestamp is None
        assert manager._mock_session.commit.called

    def test_reset_watermark_noop_when_missing(self, manager):
        """Should do nothing if no watermark exists."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        # Should not raise
        manager.reset_watermark("non-existent-pipeline")
        assert not manager._mock_session.commit.called


class TestWatermarkManagerTimestamp:
    """Tests for get_last_processed_timestamp."""

    def test_get_last_processed_timestamp_returns_datetime(self, manager):
        """Should return the timestamp from the watermark."""
        mock_wm = MagicMock()
        mock_wm.pipeline_name = "test-pipeline"
        mock_wm.last_processed_file = "file.csv"
        mock_wm.last_processed_timestamp = datetime(2026, 7, 1, 8, 0, 0)
        mock_wm.updated_at = datetime(2026, 7, 1, 8, 0, 0)

        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            mock_wm
        )

        ts = manager.get_last_processed_timestamp("test-pipeline")
        assert ts == datetime(2026, 7, 1, 8, 0, 0)

    def test_get_last_processed_timestamp_returns_none(self, manager):
        """Should return None when no watermark."""
        manager._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        ts = manager.get_last_processed_timestamp("test-pipeline")
        assert ts is None
