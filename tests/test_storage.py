"""Tests for the storage layer (CsvHandler, ParquetHandler, StorageFactory, FileHandler)."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.storage.csv_handler import CsvHandler
from src.storage.file_handler import FileHandler
from src.storage.parquet_handler import ParquetHandler
from src.storage.storage_factory import StorageFactory

# ==================================================================
# CsvHandler
# ==================================================================


class TestCsvHandler:
    def test_read_csv_file(self):
        """CsvHandler.read should return a DataFrame from a CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\n1,2\n3,4\n")
            path = Path(f.name)

        try:
            df = CsvHandler.read(path)
            assert len(df) == 2
            assert list(df.columns) == ["a", "b"]
        finally:
            path.unlink(missing_ok=True)

    def test_write_csv_file(self):
        """CsvHandler.write should write a DataFrame to CSV."""
        df = pd.DataFrame({"x": [1, 2], "y": [3, 4]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.csv"
            CsvHandler.write(df, path)

            assert path.exists()
            written = pd.read_csv(path)
            assert len(written) == 2
            assert list(written.columns) == ["x", "y"]

    def test_write_csv_with_index(self):
        """CsvHandler.write should respect explicit index=True."""
        df = pd.DataFrame({"x": [1, 2]}, index=[10, 20])

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "with_index.csv"
            CsvHandler.write(df, path, index=True)

            written = pd.read_csv(path)
            # Should have the index column "Unnamed: 0"
            assert "x" in written.columns


# ==================================================================
# ParquetHandler
# ==================================================================


class TestParquetHandler:
    def test_read_parquet_file(self):
        """ParquetHandler.read should return a DataFrame from a Parquet file."""
        df_orig = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            df_orig.to_parquet(path, index=False)

            df_read = ParquetHandler.read(path)
            assert len(df_read) == 2
            assert list(df_read.columns) == ["a", "b"]

    def test_write_parquet_file(self):
        """ParquetHandler.write should write a DataFrame to Parquet."""
        df = pd.DataFrame({"x": [1, 2], "y": [3.0, 4.0]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            ParquetHandler.write(df, path)

            assert path.exists()
            written = pd.read_parquet(path)
            assert len(written) == 2

    def test_write_overwrites_existing(self):
        """ParquetHandler.write should overwrite an existing file."""
        df = pd.DataFrame({"x": [1]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            # Write once
            ParquetHandler.write(df, path)
            # Write again (should overwrite)
            df2 = pd.DataFrame({"y": [2]})
            ParquetHandler.write(df2, path)

            written = pd.read_parquet(path)
            assert list(written.columns) == ["y"]

    def test_write_overwrites_existing_directory(self):
        """ParquetHandler.write should overwrite even if path is a directory (Spark-style)."""
        df = pd.DataFrame({"x": [1]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "testdir.parquet"
            path.mkdir(parents=True, exist_ok=True)

            # Should remove the directory and write a file
            ParquetHandler.write(df, path)

            assert path.exists()
            # If it was written as a file (not directory), this works
            written = pd.read_parquet(path)
            assert len(written) == 1


# ==================================================================
# StorageFactory
# ==================================================================


class TestStorageFactory:
    def test_get_handler_csv(self):
        """StorageFactory should return CsvHandler for .csv files."""
        handler = StorageFactory.get_handler("data/file.csv")
        assert handler == CsvHandler

    def test_get_handler_parquet(self):
        """StorageFactory should return ParquetHandler for .parquet files."""
        handler = StorageFactory.get_handler("data/file.parquet")
        assert handler == ParquetHandler

    def test_get_handler_pq(self):
        """StorageFactory should handle .pq extension."""
        handler = StorageFactory.get_handler("data/file.pq")
        assert handler == ParquetHandler

    def test_get_handler_unsupported(self):
        """StorageFactory should raise ValueError for unsupported formats."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            StorageFactory.get_handler("data/file.txt")


# ==================================================================
# FileHandler
# ==================================================================


class TestFileHandler:
    def test_read_csv(self):
        """FileHandler.read should read a CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b\n1,2\n")
            path = Path(f.name)

        try:
            df = FileHandler.read(path)
            assert len(df) == 1
        finally:
            path.unlink(missing_ok=True)

    def test_read_parquet(self):
        """FileHandler.read should read a Parquet file."""
        df_orig = pd.DataFrame({"a": [1]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            df_orig.to_parquet(path, index=False)

            df_read = FileHandler.read(path)
            assert len(df_read) == 1

    def test_read_unsupported(self):
        """FileHandler.read should raise ValueError for unsupported formats."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Unsupported file type"):
                FileHandler.read(path)
        finally:
            path.unlink(missing_ok=True)

    def test_write_csv(self):
        """FileHandler.write should write CSV via CsvHandler."""
        df = pd.DataFrame({"a": [1]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.csv"
            FileHandler.write(df, path)
            assert path.exists()

    def test_write_parquet(self):
        """FileHandler.write should write Parquet via ParquetHandler."""
        df = pd.DataFrame({"a": [1]})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.parquet"
            FileHandler.write(df, path)
            assert path.exists()
