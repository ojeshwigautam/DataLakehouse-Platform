"""Tests for Gold layer validation (validate_gold and individual validators)."""

import pytest

from src.validation.gold_validation import (
    validate_daily_sales,
    validate_delivery_summary,
    validate_gold,
    validate_monthly_sales,
    validate_payment_summary,
    validate_seller_performance,
    validate_top_products,
    validate_top_states,
)

# ==================================================================
# validate_daily_sales
# ==================================================================


@pytest.mark.mock_df("sample_daily_sales_df")
def test_daily_sales_success(mock_file_read):
    validate_daily_sales()  # should not raise


@pytest.mark.mock_df("sample_daily_sales_df")
def test_daily_sales_missing_column(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df = df.drop(columns=["total_orders"])
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_daily_sales()


@pytest.mark.mock_df("sample_daily_sales_df")
def test_daily_sales_negative_revenue(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "total_revenue"] = -100.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_daily_sales()


# ==================================================================
# validate_monthly_sales
# ==================================================================


@pytest.mark.mock_df("sample_monthly_sales_df")
def test_monthly_sales_success(mock_file_read):
    validate_monthly_sales()


@pytest.mark.mock_df("sample_monthly_sales_df")
def test_monthly_sales_missing_column(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df = df.drop(columns=["order_month"])
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_monthly_sales()


# ==================================================================
# validate_payment_summary
# ==================================================================


@pytest.mark.mock_df("sample_payment_summary_df")
def test_payment_summary_success(mock_file_read):
    validate_payment_summary()


@pytest.mark.mock_df("sample_payment_summary_df")
def test_payment_summary_negative_amount(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "total_amount"] = -50.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_payment_summary()


# ==================================================================
# validate_seller_performance
# ==================================================================


@pytest.mark.mock_df("sample_seller_performance_df")
def test_seller_performance_success(mock_file_read):
    validate_seller_performance()


@pytest.mark.mock_df("sample_seller_performance_df")
def test_seller_performance_negative_revenue(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "total_revenue"] = -1.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_seller_performance()


# ==================================================================
# validate_top_products
# ==================================================================


@pytest.mark.mock_df("sample_top_products_df")
def test_top_products_success(mock_file_read):
    validate_top_products()


@pytest.mark.mock_df("sample_top_products_df")
def test_top_products_negative_avg_price(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "average_price"] = -10.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_top_products()


# ==================================================================
# validate_top_states
# ==================================================================


@pytest.mark.mock_df("sample_top_states_df")
def test_top_states_success(mock_file_read):
    validate_top_states()


@pytest.mark.mock_df("sample_top_states_df")
def test_top_states_null_state(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "customer_state"] = None
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_top_states()


# ==================================================================
# validate_delivery_summary
# ==================================================================


@pytest.mark.mock_df("sample_delivery_summary_df")
def test_delivery_summary_success(mock_file_read):
    validate_delivery_summary()


@pytest.mark.mock_df("sample_delivery_summary_df")
def test_delivery_summary_negative_days(mock_file_read):
    from src.storage.file_handler import FileHandler

    df = FileHandler.read.return_value.copy()
    df.loc[0, "average_delivery_days"] = -1.0
    FileHandler.read.return_value = df

    with pytest.raises(Exception):
        validate_delivery_summary()


# ==================================================================
# validate_gold (aggregate wrapper)
# ==================================================================


@pytest.mark.mock_df("sample_daily_sales_df")
def test_validate_gold_success(
    mock_file_read,
    mock_save_validation_report,
    sample_monthly_sales_df,
    sample_payment_summary_df,
    sample_seller_performance_df,
    sample_top_products_df,
    sample_top_states_df,
    sample_delivery_summary_df,
):
    """All 7 valid datasets should pass validate_gold without error."""
    from src.storage.file_handler import FileHandler

    # We need to provide the correct DataFrame for each call.
    # Each validator calls FileHandler.read() using a different path constant.
    # We sequence returns so the first call returns daily_sales, second monthly, etc.
    mock_read = FileHandler.read
    mock_read.side_effect = [
        FileHandler.read.return_value,  # daily_sales
        sample_monthly_sales_df,  # monthly_sales
        sample_payment_summary_df,
        sample_seller_performance_df,
        sample_top_products_df,
        sample_top_states_df,
        sample_delivery_summary_df,
    ]

    validate_gold()

    mock_save_validation_report["gold"].assert_called_once_with(
        "gold", True, "All Gold datasets validated successfully."
    )


@pytest.mark.mock_df("sample_daily_sales_df")
def test_validate_gold_failure(
    mock_file_read,
    mock_save_validation_report,
    sample_monthly_sales_df,
    sample_payment_summary_df,
    sample_seller_performance_df,
    sample_top_products_df,
    sample_top_states_df,
    sample_delivery_summary_df,
):
    """If one dataset fails, validate_gold should raise and report failure."""
    from src.storage.file_handler import FileHandler

    # Make monthly_sales (2nd call) invalid by returning an empty DF
    bad_df = sample_monthly_sales_df.drop(columns=["order_month"])

    mock_read = FileHandler.read
    mock_read.side_effect = [
        FileHandler.read.return_value,  # daily_sales — valid
        bad_df,  # monthly_sales — missing column → error
        sample_payment_summary_df,
        sample_seller_performance_df,
        sample_top_products_df,
        sample_top_states_df,
        sample_delivery_summary_df,
    ]

    with pytest.raises(Exception):
        validate_gold()
