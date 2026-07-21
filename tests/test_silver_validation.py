"""Tests for Silver layer validation (validate_silver)."""

import pandas as pd
import pytest

from src.validation.silver_validation import validate_silver

# ------------------------------------------------------------------
# Helper: produce a large-enough valid DataFrame (>= 100000 rows)
# ------------------------------------------------------------------


def _large_valid_df(base_df):
    """Repeat a small valid DataFrame until it has at least 100 000 rows,
    making repeated rows unique so that the duplicate check does not fail.

    Preserves the original order_id values from base_df so that test
    mutations (e.g. null injection, duplicate rows) are not overwritten.
    Only newly repeated (copied) rows get unique order_id values.
    """
    repeats = 100_000 // len(base_df) + 1
    large = pd.concat([base_df] * repeats, ignore_index=True)
    n = len(base_df)
    # Only reassign order_id for the repeated copies (rows beyond the original set)
    for i in range(n, len(large)):
        large.at[i, "order_id"] = f"ord_{i:06d}"
    return large


# ------------------------------------------------------------------
# Happy-path: valid Silver dataset
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_success(mock_file_read, mock_save_validation_report):
    """A valid silver DataFrame with enough rows should pass."""
    from src.storage.file_handler import FileHandler

    FileHandler.read.return_value = _large_valid_df(FileHandler.read.return_value)

    # Should not raise
    validate_silver("dummy/path.parquet")

    mock_save_validation_report["silver"].assert_called_once_with(
        "silver", True, "Silver validation passed successfully."
    )


# ------------------------------------------------------------------
# Edge cases: row count
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_row_count_too_low(mock_file_read, mock_save_validation_report):
    """A DataFrame with fewer than 100 000 rows should raise ValueError."""
    with pytest.raises(ValueError, match="row count is lower than expected"):
        validate_silver("dummy/path.parquet")

    mock_save_validation_report["silver"].assert_called_once_with(
        "silver", False, "Unexpected row count: 3"
    )


# ------------------------------------------------------------------
# Edge cases: duplicate rows
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_duplicate_rows(mock_file_read, mock_save_validation_report):
    """Exact duplicate rows should raise ValueError."""
    from src.storage.file_handler import FileHandler

    base = FileHandler.read.return_value
    # Create duplicates by concatenating the first row twice
    dupe = pd.concat([base, base.iloc[[0]]], ignore_index=True)
    FileHandler.read.return_value = _large_valid_df(dupe)

    with pytest.raises(ValueError, match="duplicate rows"):
        validate_silver("dummy/path.parquet")

    mock_save_validation_report["silver"].assert_called_once_with(
        "silver", False, "1 exact duplicate rows found."
    )


# ------------------------------------------------------------------
# Edge cases: invalid order_status
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_invalid_order_status(
    mock_file_read, mock_save_validation_report
):
    """An invalid order_status value should raise ValueError."""
    from src.storage.file_handler import FileHandler

    base = FileHandler.read.return_value.copy()
    base.loc[0, "order_status"] = "INVALID_STATUS"
    FileHandler.read.return_value = _large_valid_df(base)

    with pytest.raises(ValueError, match="Invalid order_status"):
        validate_silver("dummy/path.parquet")


# ------------------------------------------------------------------
# Schema validation: missing required column
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_missing_column(mock_file_read, mock_save_validation_report):
    """Missing a required column should raise an exception."""
    from src.storage.file_handler import FileHandler

    base = FileHandler.read.return_value.copy()
    base = base.drop(columns=["customer_id"])
    FileHandler.read.return_value = _large_valid_df(base)

    with pytest.raises(Exception):
        validate_silver("dummy/path.parquet")


# ------------------------------------------------------------------
# Schema validation: null in non-nullable column
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_null_in_required_column(
    mock_file_read, mock_save_validation_report
):
    """A null in a non-nullable column should raise an exception."""
    from src.storage.file_handler import FileHandler

    base = FileHandler.read.return_value.copy()
    base.loc[0, "order_id"] = None
    FileHandler.read.return_value = _large_valid_df(base)

    with pytest.raises(Exception):
        validate_silver("dummy/path.parquet")


# ------------------------------------------------------------------
# Schema validation: negative monetary values
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_silver_df")
def test_validate_silver_negative_price(mock_file_read, mock_save_validation_report):
    """A negative price should fail the Check.ge(0) constraint."""
    from src.storage.file_handler import FileHandler

    base = FileHandler.read.return_value.copy()
    base.loc[0, "price"] = -1.0
    FileHandler.read.return_value = _large_valid_df(base)

    with pytest.raises(Exception):
        validate_silver("dummy/path.parquet")
