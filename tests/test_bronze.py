"""Tests for the Bronze layer (save_to_bronze)."""

import pandas as pd

from src.bronze.save_to_bronze import save_to_bronze


class TestSaveToBronze:
    def test_saves_parquet_file(self, tmp_path):
        """save_to_bronze should save a DataFrame as Parquet."""
        df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.0]})
        output_dir = tmp_path / "bronze"

        save_to_bronze(df, output_dir)

        expected = output_dir / "bronze_orders.parquet"
        assert expected.exists()

        written = pd.read_parquet(expected)
        assert len(written) == 2

    def test_creates_output_directory(self, tmp_path):
        """save_to_bronze should create the output directory if it doesn't exist."""
        df = pd.DataFrame({"x": [1]})
        output_dir = tmp_path / "nonexistent" / "bronze"

        save_to_bronze(df, output_dir)

        assert output_dir.exists()
        assert (output_dir / "bronze_orders.parquet").exists()
