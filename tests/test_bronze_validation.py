"""Tests for Bronze layer validation (validate_bronze)."""

import pandas as pd
import pytest

from src.validation.bronze_validation import validate_bronze

# ------------------------------------------------------------------
# Happy-path: valid Bronze dataset
# ------------------------------------------------------------------


@pytest.mark.mock_df("large_bronze_df")
def test_validate_bronze_success(mock_file_read, mock_save_validation_report):
    """A valid Bronze DataFrame should pass validation without error."""
    # This should not raise
    validate_bronze("dummy/path.parquet")

    mock_save_validation_report["bronze"].assert_called_once_with(
        "bronze", True, "Bronze validation passed."
    )


# ------------------------------------------------------------------
# Edge cases: data issues
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_row_count_too_low(mock_file_read, mock_save_validation_report):
    """A DataFrame with fewer than 100 000 rows should raise ValueError."""
    # The mock returns only 3 rows — well below 100 000
    from src.validation.bronze_validation import validate_bronze

    with pytest.raises(ValueError, match="row count is lower than expected"):
        validate_bronze("dummy/path.parquet")

    mock_save_validation_report["bronze"].assert_called_once_with(
        "bronze", False, "Unexpected row count: 3"
    )


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_empty_dataframe(mock_file_read, mock_save_validation_report):
    """An empty DataFrame should raise ValueError."""
    # Override the FileHandler.read return with an empty DF
    from src.storage.file_handler import FileHandler

    FileHandler.read.return_value = pd.DataFrame()

    with pytest.raises(ValueError, match="Dataset is empty"):
        validate_bronze("dummy/path.parquet")

    mock_save_validation_report["bronze"].assert_called_once_with(
        "bronze", False, "Dataset is empty."
    )


# ------------------------------------------------------------------
# Schema validation: missing / null required columns
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_missing_column(mock_file_read, mock_save_validation_report):
    """Missing a required column should raise a SchemaError."""
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df = df.drop(columns=["order_status"])
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_bronze("dummy/path.parquet")


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_null_in_required_column(
    mock_file_read, mock_save_validation_report
):
    """A null value in a non-nullable column should raise a SchemaError."""
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "order_id"] = None
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_bronze("dummy/path.parquet")


# ------------------------------------------------------------------
# Schema validation: negative monetary values
# ------------------------------------------------------------------


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_negative_price(mock_file_read, mock_save_validation_report):
    """A negative price should fail the Check.ge(0) constraint."""
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "price"] = -50.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_bronze("dummy/path.parquet")


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_negative_freight(mock_file_read, mock_save_validation_report):
    """A negative freight_value should fail the Check.ge(0) constraint."""
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "freight_value"] = -5.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_bronze("dummy/path.parquet")


@pytest.mark.mock_df("sample_bronze_df")
def test_validate_bronze_negative_payment(mock_file_read, mock_save_validation_report):
    """A negative payment_value should fail the Check.ge(0) constraint."""
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "payment_value"] = -10.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_bronze("dummy/path.parquet")
