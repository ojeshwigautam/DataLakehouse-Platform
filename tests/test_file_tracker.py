"""Tests for FileTracker."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.metadata.file_tracker import FileTracker


@pytest.fixture
def tracker():
    """FileTracker with mocked database."""
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_session.__enter__.return_value = mock_session
    mock_session.__exit__.return_value = None

    with patch(
        "src.metadata.file_tracker.get_database_engine",
        return_value=mock_engine,
    ):
        with patch(
            "src.metadata.file_tracker.Session",
            return_value=mock_session,
        ):
            trk = FileTracker()
            trk._mock_engine = mock_engine
            trk._mock_session = mock_session
            yield trk


@pytest.fixture
def temp_file():
    """Create a temporary file for checksum testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("col1,col2\n1,test\n2,data\n")
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink(missing_ok=True)


class TestFileTrackerChecksum:
    """Tests for checksum computation."""

    def test_compute_checksum_returns_string(self, tracker, temp_file):
        """Should return a hex string."""
        checksum = tracker.compute_checksum(temp_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 hex length

    def test_compute_checksum_is_deterministic(self, tracker, temp_file):
        """Should return same checksum for same file content."""
        c1 = tracker.compute_checksum(temp_file)
        c2 = tracker.compute_checksum(temp_file)
        assert c1 == c2

    def test_compute_checksum_different_files_differ(self, tracker):
        """Different content should produce different checksums."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f1:
            f1.write("content_a\n")
            p1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f2:
            f2.write("content_b\n")
            p2 = Path(f2.name)

        try:
            c1 = tracker.compute_checksum(p1)
            c2 = tracker.compute_checksum(p2)
            assert c1 != c2
        finally:
            p1.unlink(missing_ok=True)
            p2.unlink(missing_ok=True)


class TestFileTrackerDuplicateDetection:
    """Tests for duplicate file detection."""

    def test_is_processed_returns_false_when_not_found(self, tracker):
        """Should return False when no matching record exists."""
        tracker._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        result = tracker.is_processed("test.csv", "abc123")
        assert result is False

    def test_is_processed_returns_true_when_found(self, tracker):
        """Should return True when matching SUCCESS record exists."""
        tracker._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock()
        )

        result = tracker.is_processed("test.csv", "abc123")
        assert result is True

    def test_mark_processed_adds_record(self, tracker, temp_file):
        """Should add ProcessedFile record and return checksum."""
        checksum = tracker.mark_processed(
            file_name=temp_file.name,
            file_path=temp_file,
            run_id="test-run-id",
            status="SUCCESS",
        )

        assert tracker._mock_session.add.called
        assert tracker._mock_session.commit.called
        assert isinstance(checksum, str)
        assert len(checksum) == 64

    def test_prevent_duplicate_returns_false_first_time(self, tracker, temp_file):
        """Should return (False, checksum) for new files without marking."""
        tracker._mock_session.query.return_value.filter_by.return_value.first.return_value = (
            None
        )

        was_processed, checksum = tracker.prevent_duplicate(
            file_path=temp_file,
        )

        assert was_processed is False
        assert isinstance(checksum, str)
        # prevent_duplicate should NOT mark the file — the caller does that
        assert not tracker._mock_session.add.called

    def test_prevent_duplicate_returns_true_for_duplicate(self, tracker, temp_file):
        """Should return (True, checksum) for already-processed files.

        The prevent_duplicate method:
        1. Computes checksum (no DB call)
        2. Calls is_processed (DB call) — we mock it to return True
        """
        tracker._mock_session.query.return_value.filter_by.return_value.first.side_effect = [
            MagicMock(),  # is_processed call  -> found, return Truthy -> True
        ]

        was_processed, checksum = tracker.prevent_duplicate(
            file_path=temp_file,
        )

        assert was_processed is True
        assert isinstance(checksum, str)
        # prevent_duplicate should NOT mark the file — just check
        assert not tracker._mock_session.add.called
