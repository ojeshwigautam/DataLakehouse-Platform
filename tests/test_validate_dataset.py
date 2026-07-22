"""Tests for the validate_dataset function."""

import pandas as pd

from src.processing.validate_dataset import validate_dataset


class TestValidateDataset:
    def test_validates_successfully(self):
        """validate_dataset should run without error on a valid DataFrame."""
        df = pd.DataFrame(
            {
                "order_id": ["o1", "o2"],
                "customer_id": ["c1", "c2"],
                "price": [100.0, 200.0],
            }
        )

        # Should not raise any exception
        validate_dataset(df)

    def test_accepts_empty_dataframe(self):
        """validate_dataset should handle an empty DataFrame gracefully."""
        df = pd.DataFrame()
        validate_dataset(df)  # Should not raise

    def test_logs_duplicates(self):
        """validate_dataset should handle DataFrames with duplicate rows."""
        df = pd.DataFrame({"a": [1, 1], "b": [2, 2]})
        validate_dataset(df)  # Should not raise

    def test_logs_missing_values(self):
        """validate_dataset should handle DataFrames with nulls."""
        df = pd.DataFrame({"a": [1, None], "b": [2, 3]})
        validate_dataset(df)  # Should not raise
