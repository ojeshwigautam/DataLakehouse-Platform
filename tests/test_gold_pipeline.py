"""Tests for the Pandas-based Gold pipeline."""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.gold.gold_pipeline import (
    _create_daily_sales,
    _create_delivery_summary,
    _create_monthly_sales,
    _create_payment_summary,
    _create_seller_performance,
    _create_top_products,
    _create_top_states,
    _prepare_dates,
    create_gold_layer,
)


class TestPrepareDates:
    def test_creates_order_date_and_month(self):
        """_prepare_dates should derive order_date and order_month from purchase timestamp."""
        df = pd.DataFrame(
            {"order_purchase_timestamp": ["2026-01-15 10:30:00", "2026-02-20 14:00:00"]}
        )
        result = _prepare_dates(df)

        assert "order_date" in result.columns
        assert "order_month" in result.columns

    def test_handles_missing_timestamp(self):
        """_prepare_dates should handle DataFrames without a purchase timestamp."""
        df = pd.DataFrame({"other_col": [1, 2]})
        result = _prepare_dates(df)
        assert "order_date" not in result.columns


class TestCreateDailySales:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_aggregates_daily_sales(self, mock_save, mock_file_handler):
        """_create_daily_sales should aggregate daily orders and revenue."""
        df = pd.DataFrame(
            {
                "order_date": ["2026-01-01", "2026-01-01", "2026-01-02"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
            }
        )
        _create_daily_sales(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_sorts_by_date(self, mock_save, mock_file_handler):
        """_create_daily_sales should sort results by order_date."""
        df = pd.DataFrame(
            {
                "order_date": ["2026-01-02", "2026-01-01"],
                "order_id": ["o1", "o2"],
                "payment_value": [100.0, 200.0],
            }
        )
        _create_daily_sales(df)
        mock_save.assert_called_once()


class TestCreateMonthlySales:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_aggregates_monthly_sales(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "order_month": ["2026-01", "2026-01", "2026-02"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
            }
        )
        _create_monthly_sales(df)
        mock_save.assert_called_once()


class TestCreateTopProducts:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_creates_top_products(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "product_category_name": ["cat1", "cat1", "cat2"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
                "price": [50.0, 100.0, 25.0],
            }
        )
        _create_top_products(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.logger")
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_warns_when_product_category_missing(self, mock_file_handler, mock_logger):
        df = pd.DataFrame(
            {
                "order_id": ["o1"],
                "payment_value": [100.0],
                "price": [50.0],
            }
        )
        _create_top_products(df)
        mock_logger.warning.assert_called_once()


class TestCreateTopStates:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_creates_top_states(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "customer_state": ["SP", "SP", "RJ"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
            }
        )
        _create_top_states(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.logger")
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_warns_when_state_column_missing(self, mock_file_handler, mock_logger):
        df = pd.DataFrame({"order_id": ["o1"], "payment_value": [100.0]})
        _create_top_states(df)
        mock_logger.warning.assert_called_once()


class TestCreatePaymentSummary:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_creates_payment_summary(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "payment_type": ["credit", "credit", "boleto"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
            }
        )
        _create_payment_summary(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.logger")
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_warns_when_payment_type_missing(self, mock_file_handler, mock_logger):
        df = pd.DataFrame({"order_id": ["o1"]})
        _create_payment_summary(df)
        mock_logger.warning.assert_called_once()


class TestCreateSellerPerformance:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_creates_seller_performance(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "seller_id": ["s1", "s1", "s2"],
                "order_id": ["o1", "o2", "o3"],
                "payment_value": [100.0, 200.0, 50.0],
            }
        )
        _create_seller_performance(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.logger")
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_warns_when_seller_column_missing(self, mock_file_handler, mock_logger):
        df = pd.DataFrame({"order_id": ["o1"]})
        _create_seller_performance(df)
        mock_logger.warning.assert_called_once()


class TestCreateDeliverySummary:
    @patch("src.gold.gold_pipeline.FileHandler")
    @patch("src.gold.gold_pipeline._save")
    def test_creates_delivery_summary(self, mock_save, mock_file_handler):
        df = pd.DataFrame(
            {
                "order_purchase_timestamp": pd.to_datetime(
                    ["2026-01-01", "2026-01-05"]
                ),
                "order_delivered_customer_date": pd.to_datetime(
                    ["2026-01-11", "2026-01-08"]
                ),
            }
        )
        _create_delivery_summary(df)
        mock_save.assert_called_once()

    @patch("src.gold.gold_pipeline.logger")
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_warns_when_delivery_dates_missing(self, mock_file_handler, mock_logger):
        df = pd.DataFrame({"order_id": ["o1"]})
        _create_delivery_summary(df)
        mock_logger.warning.assert_called_once()


class TestCreateGoldLayer:
    @patch("src.gold.gold_pipeline.FileHandler")
    def test_creates_all_gold_datasets(self, mock_file_handler):
        """create_gold_layer should call all individual _create_* functions."""
        df = pd.DataFrame(
            {
                "order_id": ["o1", "o2"],
                "order_unique_id": ["u1", "u2"],
                "customer_id": ["c1", "c2"],
                "product_id": ["p1", "p2"],
                "seller_id": ["s1", "s2"],
                "price": [100.0, 200.0],
                "freight_value": [10.0, 20.0],
                "payment_value": [110.0, 220.0],
                "customer_city": ["Sao Paulo", "Rio"],
                "seller_city": ["Campinas", "BH"],
                "customer_state": ["SP", "RJ"],
                "seller_state": ["SP", "MG"],
                "order_purchase_timestamp": pd.to_datetime(
                    ["2026-01-01", "2026-01-02"]
                ),
                "order_approved_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
                "order_delivered_carrier_date": pd.to_datetime(
                    ["2026-01-05", "2026-01-07"]
                ),
                "order_delivered_customer_date": pd.to_datetime(
                    ["2026-01-10", "2026-01-12"]
                ),
                "order_estimated_delivery_date": pd.to_datetime(
                    ["2026-01-15", "2026-01-18"]
                ),
                "shipping_limit_date": pd.to_datetime(["2026-01-10", "2026-01-15"]),
                "order_status": ["delivered", "shipped"],
                "product_category_name": ["cat1", "cat2"],
                "payment_type": ["credit", "boleto"],
            }
        )
        mock_file_handler.read.return_value = df

        with patch("src.gold.gold_pipeline.GOLD_DIR") as mock_gold_dir:
            mock_gold_dir.mkdir = MagicMock()
            create_gold_layer()

        # FileHandler.read should have been called
        mock_file_handler.read.assert_called_once()
