import os
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from src.spark.session import get_spark

# ------------------------------------------------------------------
# Spark Session Fixture (session-scoped)
# ------------------------------------------------------------------


@pytest.fixture(scope="session")
def spark():
    spark = get_spark()
    yield spark
    spark.stop()


# ------------------------------------------------------------------
# Shared Sample DataFrames for Validation Tests
# ------------------------------------------------------------------


@pytest.fixture
def sample_bronze_df():
    """A valid Bronze-layer DataFrame matching BronzeSchema."""
    return pd.DataFrame(
        {
            "order_id": ["ord_001", "ord_002", "ord_003"],
            "order_item_id": [1, 1, 2],
            "customer_id": ["cust_001", "cust_002", "cust_003"],
            "product_id": ["prod_001", "prod_002", "prod_003"],
            "seller_id": ["sell_001", "sell_002", "sell_003"],
            "price": [100.0, 200.0, 150.0],
            "freight_value": [10.0, 20.0, 15.0],
            "payment_value": [110.0, 220.0, 165.0],
            "order_purchase_timestamp": [
                "2026-01-01 10:00:00",
                "2026-01-02 11:00:00",
                "2026-01-03 12:00:00",
            ],
            "order_status": [
                "delivered",
                "shipped",
                "processing",
            ],
        }
    )


@pytest.fixture
def sample_silver_df():
    """A valid Silver-layer DataFrame matching SilverSchema."""
    return pd.DataFrame(
        {
            "order_id": ["ord_001", "ord_002", "ord_003"],
            "order_item_id": [1, 1, 2],
            "customer_id": ["cust_001", "cust_002", "cust_003"],
            "product_id": ["prod_001", "prod_002", "prod_003"],
            "seller_id": ["sell_001", "sell_002", "sell_003"],
            "price": [100.0, 200.0, 150.0],
            "freight_value": [10.0, 20.0, 15.0],
            "payment_value": [110.0, 220.0, 165.0],
            "order_purchase_timestamp": [
                "2026-01-01 10:00:00",
                "2026-01-02 11:00:00",
                "2026-01-03 12:00:00",
            ],
            "order_status": [
                "delivered",
                "shipped",
                "processing",
            ],
        }
    )


@pytest.fixture
def large_bronze_df():
    """A large Bronze-layer DataFrame with >100000 rows for success tests."""
    base = pd.DataFrame(
        {
            "order_id": [f"ord_{i:06d}" for i in range(100_000)],
            "order_item_id": [1] * 100_000,
            "customer_id": [f"cust_{i:06d}" for i in range(100_000)],
            "product_id": [f"prod_{i:06d}" for i in range(100_000)],
            "seller_id": [f"sell_{i:06d}" for i in range(100_000)],
            "price": [100.0] * 100_000,
            "freight_value": [10.0] * 100_000,
            "payment_value": [110.0] * 100_000,
            "order_purchase_timestamp": ["2026-01-01 10:00:00"] * 100_000,
            "order_status": ["delivered"] * 100_000,
        }
    )
    return base


@pytest.fixture
def sample_daily_sales_df():
    """A valid daily_sales Gold DataFrame."""
    return pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "total_orders": [10, 20],
            "total_revenue": [1000.0, 2500.0],
            "average_order_value": [100.0, 125.0],
        }
    )


@pytest.fixture
def sample_monthly_sales_df():
    """A valid monthly_sales Gold DataFrame."""
    return pd.DataFrame(
        {
            "order_month": ["2026-01", "2026-02"],
            "total_orders": [100, 150],
            "total_revenue": [12000.0, 18000.0],
            "average_order_value": [120.0, 120.0],
        }
    )


@pytest.fixture
def sample_payment_summary_df():
    """A valid payment_summary Gold DataFrame."""
    return pd.DataFrame(
        {
            "payment_type": ["credit_card", "boleto"],
            "total_transactions": [500, 200],
            "total_amount": [50000.0, 15000.0],
            "average_payment": [100.0, 75.0],
        }
    )


@pytest.fixture
def sample_seller_performance_df():
    """A valid seller_performance Gold DataFrame."""
    return pd.DataFrame(
        {
            "seller_id": ["sell_001", "sell_002"],
            "total_orders": [50, 30],
            "total_revenue": [7500.0, 4500.0],
            "average_order_value": [150.0, 150.0],
        }
    )


@pytest.fixture
def sample_top_products_df():
    """A valid top_products Gold DataFrame."""
    return pd.DataFrame(
        {
            "product_category_name": ["electronics", "books"],
            "total_orders": [200, 150],
            "total_revenue": [40000.0, 7500.0],
            "average_price": [200.0, 50.0],
        }
    )


@pytest.fixture
def sample_top_states_df():
    """A valid top_states Gold DataFrame."""
    return pd.DataFrame(
        {
            "customer_state": ["SP", "RJ"],
            "total_orders": [500, 300],
            "total_revenue": [75000.0, 45000.0],
        }
    )


@pytest.fixture
def sample_delivery_summary_df():
    """A valid delivery_summary Gold DataFrame."""
    return pd.DataFrame(
        {
            "average_delivery_days": [5.5],
            "minimum_delivery_days": [2.0],
            "maximum_delivery_days": [15.0],
        }
    )


# ------------------------------------------------------------------
# Mock helpers for validation tests
# ------------------------------------------------------------------


@pytest.fixture
def mock_file_read(request):
    """Patch src.storage.file_handler.FileHandler.read to return a
    DataFrame specified via the ``mock_df`` marker, or a default
    valid bronze DataFrame.

    Usage:
        @pytest.mark.mock_df("sample_silver_df")
        def test_something(mock_file_read):
            ...
    """
    marker = request.node.get_closest_marker("mock_df")
    fixture_name = marker.args[0] if marker else "sample_bronze_df"
    df = request.getfixturevalue(fixture_name)

    with patch(
        "src.storage.file_handler.FileHandler.read",
        return_value=df,
    ) as mock:
        yield mock


@pytest.fixture
def mock_save_validation_report():
    """Patch save_validation_report at all 3 usage locations to avoid writing to disk.

    Yields a dict with keys "bronze", "silver", "gold" so each test can
    assert calls against the correct module-level mock.
    """
    with (
        patch("src.validation.bronze_validation.save_validation_report") as mock_bronze,
        patch("src.validation.silver_validation.save_validation_report") as mock_silver,
        patch("src.validation.gold_validation.save_validation_report") as mock_gold,
    ):
        yield {
            "bronze": mock_bronze,
            "silver": mock_silver,
            "gold": mock_gold,
        }


@pytest.fixture
def mock_database_engine():
    """Patch get_database_engine to return a mock engine."""
    mock_engine = MagicMock()
    with patch(
        "src.database.connection.get_database_engine",
        return_value=mock_engine,
    ) as mock:
        yield mock


@pytest.fixture
def mock_stages():
    """Mock all pipeline stage functions to avoid side effects."""
    with (
        patch("src.pipeline.etl_pipeline.run_bronze") as mock_bronze,
        patch("src.pipeline.etl_pipeline.run_bronze_validation") as mock_bronze_val,
        patch("src.pipeline.etl_pipeline.run_silver") as mock_silver,
        patch("src.pipeline.etl_pipeline.run_silver_validation") as mock_silver_val,
        patch("src.pipeline.etl_pipeline.run_gold") as mock_gold,
        patch("src.pipeline.etl_pipeline.run_gold_validation") as mock_gold_val,
        patch("src.pipeline.etl_pipeline.run_postgres") as mock_postgres,
        patch("src.pipeline.etl_pipeline.run_postgres_validation") as mock_pg_val,
        patch(
            "src.pipeline.etl_pipeline.process_incremental_files",
            return_value=[],
        ) as mock_inc,
        patch(
            "src.pipeline.etl_pipeline.start_pipeline_audit",
            return_value="test-run-id",
        ) as mock_audit_start,
        patch(
            "src.pipeline.etl_pipeline.complete_pipeline_audit"
        ) as mock_audit_complete,
    ):
        mock_postgres.return_value = [
            "daily_sales",
            "monthly_sales",
        ]
        yield {
            "bronze": mock_bronze,
            "bronze_val": mock_bronze_val,
            "silver": mock_silver,
            "silver_val": mock_silver_val,
            "gold": mock_gold,
            "gold_val": mock_gold_val,
            "postgres": mock_postgres,
            "pg_val": mock_pg_val,
            "inc": mock_inc,
            "audit_start": mock_audit_start,
            "audit_complete": mock_audit_complete,
        }
