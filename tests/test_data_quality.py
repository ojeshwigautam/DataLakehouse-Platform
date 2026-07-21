import pandas as pd
import pytest

from src.processing.data_quality import (
    check_critical_nulls,
    check_duplicate_rows,
    check_empty_dataset,
    check_numeric_values,
    check_order_ids,
    check_required_columns,
    check_timestamp_values,
    run_data_quality_checks,
)


def create_valid_dataframe():
    """
    Create a small valid dataset for automated testing.
    """

    return pd.DataFrame(
        {
            "order_id": [
                "order_001",
                "order_002",
            ],
            "customer_id": [
                "customer_001",
                "customer_002",
            ],
            "product_id": [
                "product_001",
                "product_002",
            ],
            "seller_id": [
                "seller_001",
                "seller_002",
            ],
            "price": [
                100.0,
                200.0,
            ],
            "freight_value": [
                10.0,
                20.0,
            ],
            "payment_value": [
                110.0,
                220.0,
            ],
            "order_purchase_timestamp": [
                "2026-01-01 10:00:00",
                "2026-01-02 11:00:00",
            ],
            "order_status": [
                "delivered",
                "delivered",
            ],
        }
    )


def test_valid_dataset_not_empty():

    df = create_valid_dataframe()

    assert check_empty_dataset(df) is True


def test_empty_dataset_raises_error():

    df = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="Dataset is empty",
    ):
        check_empty_dataset(df)


def test_required_columns_pass():

    df = create_valid_dataframe()

    assert check_required_columns(df) is True


def test_missing_required_column_raises_error():

    df = create_valid_dataframe()

    df = df.drop(columns=["order_id"])

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        check_required_columns(df)


def test_duplicate_rows_check():

    df = create_valid_dataframe()

    duplicate_df = pd.concat(
        [
            df,
            df.iloc[[0]],
        ],
        ignore_index=True,
    )

    assert check_duplicate_rows(duplicate_df) is True


def test_critical_nulls_pass():

    df = create_valid_dataframe()

    assert check_critical_nulls(df) is True


def test_critical_nulls_raise_error():

    df = create_valid_dataframe()

    df.loc[
        0,
        "customer_id",
    ] = None

    with pytest.raises(
        ValueError,
        match="Critical null values detected",
    ):
        check_critical_nulls(df)


def test_numeric_values_pass():

    df = create_valid_dataframe()

    assert check_numeric_values(df) is True


def test_negative_price_raises_error():

    df = create_valid_dataframe()

    df.loc[
        0,
        "price",
    ] = -100

    with pytest.raises(
        ValueError,
        match="Negative numeric values detected",
    ):
        check_numeric_values(df)


def test_order_ids_pass():

    df = create_valid_dataframe()

    assert check_order_ids(df) is True


def test_invalid_order_id_raises_error():

    df = create_valid_dataframe()

    df.loc[
        0,
        "order_id",
    ] = None

    with pytest.raises(
        ValueError,
        match="Invalid order IDs detected",
    ):
        check_order_ids(df)


def test_timestamp_values_pass():

    df = create_valid_dataframe()

    assert check_timestamp_values(df) is True


def test_invalid_timestamp_raises_error():

    df = create_valid_dataframe()

    df.loc[
        0,
        "order_purchase_timestamp",
    ] = "invalid-date"

    with pytest.raises(
        ValueError,
        match="Invalid order purchase timestamps",
    ):
        check_timestamp_values(df)


def test_complete_data_quality_pipeline():

    df = create_valid_dataframe()

    assert run_data_quality_checks(df) is True
