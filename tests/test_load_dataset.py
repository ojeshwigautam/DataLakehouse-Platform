"""Tests for the load_dataset function."""

from pathlib import Path

import pytest

from src.ingestion.load_dataset import load_dataset


class TestLoadDataset:
    def test_loads_csv_file(self, tmp_path):
        """load_dataset should load a CSV file and return a DataFrame."""
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("col1,col2\n1,test\n2,data\n")

        df = load_dataset(csv_path)

        assert len(df) == 2
        assert list(df.columns) == ["col1", "col2"]

    def test_removes_unnamed_index_column(self, tmp_path):
        """load_dataset should drop 'Unnamed: 0' index column if present."""
        csv_path = tmp_path / "with_index.csv"
        csv_path.write_text("Unnamed: 0,col1,col2\n0,1,test\n1,2,data\n")

        df = load_dataset(csv_path)

        assert "Unnamed: 0" not in df.columns
        assert list(df.columns) == ["col1", "col2"]

    def test_raises_file_not_found(self):
        """load_dataset should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError, match="Dataset not found"):
            load_dataset(Path("/nonexistent/path.csv"))
