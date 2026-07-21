"""
Tests for the Incremental Loader orchestration.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.ingestion.incremental_loader import IncrementalLoader

# ── Fixtures ───────────────────────────────────────────────────────


@pytest.fixture
def tmp_incremental_dir() -> Path:
    """A temporary directory simulating the incremental folder."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def tmp_bronze_dir() -> Path:
    """A temporary directory simulating the bronze incremental folder."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def sample_csv_files(tmp_incremental_dir: Path) -> list:
    """Create sample CSV files in the incremental directory."""
    files = []
    for name in ["orders_2026_07_20.csv", "orders_2026_07_21.csv"]:
        path = tmp_incremental_dir / name
        path.write_text("col1,col2\n1,test\n2,data\n")
        files.append(path)
    return files


@pytest.fixture
def loader(tmp_incremental_dir: Path, tmp_bronze_dir: Path) -> IncrementalLoader:
    """An IncrementalLoader with mocked metadata components."""
    loader = IncrementalLoader(
        incremental_dir=tmp_incremental_dir,
        bronze_dir=tmp_bronze_dir,
        run_id="test-run-id",
    )
    return loader


# ── Core run() Tests ───────────────────────────────────────────────


class TestIncrementalLoader:
    def test_run_with_no_files(self, loader: IncrementalLoader):
        """Should return a result with zero new files when folder is empty."""
        result = loader.run()
        assert result.total_files_discovered == 0
        assert result.new_files_count == 0
        assert result.rows_loaded == 0
        assert result.status == "SUCCESS"

    def test_run_with_new_files(
        self, loader: IncrementalLoader, sample_csv_files: list
    ):
        """Should process new files and produce a bronze parquet."""
        # Mock FileTracker to simulate no duplicates
        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            return_value=(False, "dummychecksum"),
        ):
            with patch.object(loader._file_tracker, "mark_processed") as mock_mark:
                with patch.object(loader._metadata_mgr, "update_watermark") as mock_wm:
                    result = loader.run()

        assert result.total_files_discovered == 2
        assert result.new_files_count == 2
        assert result.rows_loaded > 0
        assert result.bronze_path is not None
        assert result.bronze_path.exists()
        assert result.status == "SUCCESS"
        assert mock_mark.call_count == 2
        assert mock_wm.called

    def test_skip_duplicate_files(
        self, loader: IncrementalLoader, sample_csv_files: list
    ):
        """Files already processed should be skipped."""
        # Mock FileTracker to simulate duplicates
        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            return_value=(True, "dummychecksum"),
        ):
            result = loader.run()

        assert result.total_files_discovered == 2
        assert result.new_files_count == 0
        assert result.rows_loaded == 0

    def test_partial_duplicates(
        self, loader: IncrementalLoader, sample_csv_files: list
    ):
        """Only unprocessed files should be loaded when some are duplicates."""
        # Simulate first file is duplicate, second is new
        call_count = [0]

        def mock_prevent_duplicate(file_path, run_id):
            call_count[0] += 1
            if call_count[0] == 1:
                return (True, "dup_checksum")  # Already processed
            return (False, "new_checksum")  # New file

        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            side_effect=mock_prevent_duplicate,
        ):
            with patch.object(loader._file_tracker, "mark_processed"):
                with patch.object(loader._metadata_mgr, "update_watermark"):
                    result = loader.run()

        assert result.total_files_discovered == 2
        assert result.new_files_count == 1
        assert result.rows_loaded > 0

    def test_merge_behavior(self, loader: IncrementalLoader, sample_csv_files: list):
        """Should append new data to existing bronze data."""
        # First, create existing bronze with some data
        existing_df = pd.DataFrame({"col1": [100, 200], "col2": ["existing", "data"]})
        loader.bronze_dir.mkdir(parents=True, exist_ok=True)
        existing_df.to_parquet(
            loader.bronze_dir / "bronze_incremental.parquet", index=False
        )

        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            return_value=(False, "newchecksum"),
        ):
            with patch.object(loader._file_tracker, "mark_processed"):
                with patch.object(loader._metadata_mgr, "update_watermark"):
                    result = loader.run()

        # Should have existing rows + new rows
        assert result.rows_loaded > 2

        # Verify merged parquet exists
        merged_df = pd.read_parquet(loader.bronze_dir / "bronze_incremental.parquet")
        assert len(merged_df) == result.rows_loaded

    def test_metadata_update_after_success(
        self, loader: IncrementalLoader, sample_csv_files: list
    ):
        """Metadata should be updated after successful processing."""
        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            return_value=(False, "newchecksum"),
        ):
            with patch.object(loader._file_tracker, "mark_processed") as mock_mark:
                with patch.object(loader._metadata_mgr, "update_watermark") as mock_wm:
                    loader.run()

        # Each new file should be marked
        assert mock_mark.call_count == 2
        # Watermark should be updated with the latest file
        mock_wm.assert_called_once()
        call_args = mock_wm.call_args[1]
        assert call_args["pipeline_name"] == "incremental_loader"

    def test_no_metadata_update_after_failure(
        self, loader: IncrementalLoader, sample_csv_files: list
    ):
        """Metadata should NOT be updated if processing fails."""

        # Simulate a failure during processing (FileHandler.read raises)
        with patch(
            "src.ingestion.incremental_loader.FileHandler.read",
            side_effect=RuntimeError("Read failed"),
        ):
            with patch.object(
                loader._file_tracker,
                "prevent_duplicate",
                return_value=(False, "newchecksum"),
            ):
                with patch.object(loader._file_tracker, "mark_processed") as mock_mark:
                    with patch.object(
                        loader._metadata_mgr, "update_watermark"
                    ) as mock_wm:
                        with pytest.raises(RuntimeError):
                            loader.run()

        # Metadata should NOT have been updated
        assert mock_mark.call_count == 0
        assert mock_wm.call_count == 0


# ── Public helper methods ──────────────────────────────────────────


class TestIncrementalLoaderHelpers:
    def test_get_new_files(self, tmp_incremental_dir: Path, tmp_bronze_dir: Path):
        """get_new_files should return only unprocessed files."""
        # Create one file
        (tmp_incremental_dir / "new_file.csv").write_text("a,b\n1,2\n")

        loader = IncrementalLoader(
            incremental_dir=tmp_incremental_dir,
            bronze_dir=tmp_bronze_dir,
        )

        with patch.object(
            loader._file_tracker,
            "prevent_duplicate",
            return_value=(False, "abc"),
        ):
            new_files = loader.get_new_files()

        assert len(new_files) == 1
        assert new_files[0].name == "new_file.csv"

    def test_load_new_files(self, tmp_incremental_dir: Path, tmp_bronze_dir: Path):
        """load_new_files should return a concatenated DataFrame."""
        file1 = tmp_incremental_dir / "f1.csv"
        file2 = tmp_incremental_dir / "f2.csv"
        file1.write_text("x\n1\n2\n")
        file2.write_text("x\n3\n4\n")

        loader = IncrementalLoader(
            incremental_dir=tmp_incremental_dir,
            bronze_dir=tmp_bronze_dir,
        )

        df = loader.load_new_files([file1, file2])
        assert len(df) == 4
        assert list(df["x"]) == [1, 2, 3, 4]

    def test_update_metadata(self, tmp_incremental_dir: Path, tmp_bronze_dir: Path):
        """update_metadata should mark files and update watermark."""
        file1 = tmp_incremental_dir / "test.csv"
        file1.write_text("a\n1\n")

        loader = IncrementalLoader(
            incremental_dir=tmp_incremental_dir,
            bronze_dir=tmp_bronze_dir,
        )

        with patch.object(loader._file_tracker, "mark_processed") as mock_mark:
            with patch.object(loader._metadata_mgr, "update_watermark") as mock_wm:
                loader.update_metadata(
                    file_paths=[file1],
                    run_id="test-run",
                    status="SUCCESS",
                )

        mock_mark.assert_called_once()
        mock_wm.assert_called_once()
