"""Tests for the Pandas-based Silver pipeline."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

from src.processing.silver_pipeline import create_silver_layer, load_bronze_data


class TestLoadBronzeData:
    @patch("src.processing.silver_pipeline.FileHandler")
    def test_loads_historical_data_only(self, mock_file_handler):
        """load_bronze_data should load historical Bronze when no incremental files exist."""
        mock_df = pd.DataFrame(
            {
                "order_id": ["o1", "o2"],
                "order_unique_id": ["u1", "u2"],
                "price": [100.0, 200.0],
                "payment_value": [110.0, 220.0],
                "freight_value": [10.0, 20.0],
                "customer_city": ["Sao Paulo", "Rio"],
                "seller_city": ["Campinas", "Belo Horizonte"],
                "customer_state": ["SP", "RJ"],
                "seller_state": ["SP", "MG"],
                "shipping_limit_date": ["2026-01-10", "2026-01-15"],
                "order_purchase_timestamp": ["2026-01-01", "2026-01-02"],
                "order_approved_at": ["2026-01-01", "2026-01-02"],
                "order_delivered_carrier_date": ["2026-01-05", "2026-01-07"],
                "order_delivered_customer_date": ["2026-01-10", "2026-01-12"],
                "order_estimated_delivery_date": ["2026-01-15", "2026-01-18"],
            }
        )
        mock_file_handler.read.return_value = mock_df

        with patch(
            "src.processing.silver_pipeline.BRONZE_INCREMENTAL_DIR",
            new_callable=MagicMock,
        ) as mock_inc_dir:
            mock_inc_dir.glob.return_value = []
            result = load_bronze_data()

        assert len(result) == 2
        assert "order_id" in result.columns

    @patch("src.processing.silver_pipeline.FileHandler")
    def test_merges_incremental_data(self, mock_file_handler):
        """load_bronze_data should merge incremental Bronze with historical."""
        historical = pd.DataFrame(
            {
                "order_id": ["o1"],
                "order_unique_id": ["u1"],
                "price": [100.0],
                "payment_value": [110.0],
                "freight_value": [10.0],
                "customer_city": ["Sao Paulo"],
                "seller_city": ["Campinas"],
                "customer_state": ["SP"],
                "seller_state": ["SP"],
                "shipping_limit_date": ["2026-01-10"],
                "order_purchase_timestamp": ["2026-01-01"],
                "order_approved_at": ["2026-01-01"],
                "order_delivered_carrier_date": ["2026-01-05"],
                "order_delivered_customer_date": ["2026-01-10"],
                "order_estimated_delivery_date": ["2026-01-15"],
            }
        )

        incremental = pd.DataFrame(
            {
                "order_id": ["o2"],
                "order_unique_id": ["u2"],
                "price": [200.0],
                "payment_value": [220.0],
                "freight_value": [20.0],
                "customer_city": ["Rio"],
                "seller_city": ["BH"],
                "customer_state": ["RJ"],
                "seller_state": ["MG"],
                "shipping_limit_date": ["2026-02-10"],
                "order_purchase_timestamp": ["2026-02-01"],
                "order_approved_at": ["2026-02-01"],
                "order_delivered_carrier_date": ["2026-02-05"],
                "order_delivered_customer_date": ["2026-02-10"],
                "order_estimated_delivery_date": ["2026-02-15"],
            }
        )
        mock_file_handler.read.side_effect = [historical, incremental]

        with patch(
            "src.processing.silver_pipeline.BRONZE_INCREMENTAL_DIR",
            new_callable=MagicMock,
        ) as mock_inc_dir:
            mock_inc_dir.glob.return_value = [Path("inc_1.parquet")]
            result = load_bronze_data()

        assert len(result) == 2


class TestCreateSilverLayer:
    @patch("src.processing.silver_pipeline.FileHandler")
    def test_creates_silver_layer(self, mock_file_handler):
        """create_silver_layer should deduplicate and clean data."""
        df = pd.DataFrame(
            {
                "order_id": ["o1", "o1", "o2"],
                "order_unique_id": ["u1", "u1", "u2"],
                "customer_id": ["c1", "c1", "c2"],
                "product_id": ["p1", "p1", "p2"],
                "seller_id": ["s1", "s1", "s2"],
                "price": [100.0, 100.0, -50.0],  # negative price should be removed
                "freight_value": [10.0, 10.0, 5.0],
                "payment_value": [110.0, 110.0, 50.0],
                "customer_city": ["Sao Paulo", "Sao Paulo", "Rio"],
                "seller_city": ["Campinas", "Campinas", "BH"],
                "customer_state": ["SP", "SP", "RJ"],
                "seller_state": ["SP", "SP", "MG"],
                "shipping_limit_date": ["2026-01-10", "2026-01-10", "2026-02-10"],
                "order_purchase_timestamp": [
                    "2026-01-01",
                    "2026-01-01",
                    "2026-02-01",
                ],
                "order_approved_at": ["2026-01-01", "2026-01-01", "2026-02-01"],
                "order_delivered_carrier_date": [
                    "2026-01-05",
                    "2026-01-05",
                    "2026-02-05",
                ],
                "order_delivered_customer_date": [
                    "2026-01-10",
                    "2026-01-10",
                    "2026-02-10",
                ],
                "order_estimated_delivery_date": [
                    "2026-01-15",
                    "2026-01-15",
                    "2026-02-15",
                ],
            }
        )
        mock_file_handler.read.return_value = df
        mock_file_handler.write = MagicMock()

        with patch(
            "src.processing.silver_pipeline.SILVER_DIR",
            new_callable=MagicMock,
        ) as mock_silver_dir:
            mock_silver_dir.__truediv__.return_value = Path(
                "silver_orders.parquet"
            ).resolve()
            create_silver_layer()

        # Should have written the silver dataset
        mock_file_handler.write.assert_called_once()
