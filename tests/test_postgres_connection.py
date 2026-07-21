"""Tests for PostgreSQL database connection (get_database_engine)."""

from unittest.mock import MagicMock, patch

import pytest

# ==================================================================
# get_database_engine
# ==================================================================


@patch("src.database.connection.create_engine")
def test_get_database_engine_success(mock_create_engine):
    """get_database_engine should return a SQLAlchemy engine when env vars are set."""
    from src.database.connection import get_database_engine

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    result = get_database_engine()

    assert result == mock_engine
    mock_create_engine.assert_called_once()


@patch("src.database.connection.create_engine")
def test_get_database_engine_url_format(mock_create_engine):
    """Verify that the database URL is built with the expected format."""
    from src.database.connection import (
        DB_HOST,
        DB_NAME,
        DB_PASSWORD,
        DB_PORT,
        DB_USER,
        get_database_engine,
    )

    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    get_database_engine()

    expected_prefix = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    actual_url = mock_create_engine.call_args[0][0]
    assert actual_url == expected_prefix


@patch("src.database.connection.create_engine")
def test_get_database_engine_failure(mock_create_engine):
    """If create_engine raises, get_database_engine should propagate the error."""
    from src.database.connection import get_database_engine

    mock_create_engine.side_effect = Exception("Connection refused")

    with pytest.raises(Exception, match="Connection refused"):
        get_database_engine()


# ==================================================================
# PostgreSQL validation (validate_postgresql_tables)
# ==================================================================


def test_validate_postgresql_tables_all_present(mock_database_engine):
    """All expected tables present should return True."""
    from src.database.validate_tables import validate_postgresql_tables

    # Set up mock inspector
    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = [
        "daily_sales",
        "monthly_sales",
        "top_products",
        "top_states",
        "payment_summary",
        "seller_performance",
        "delivery_summary",
    ]

    # Mock connection scalar returns row count
    mock_conn = MagicMock()
    mock_conn.execute.return_value.scalar.return_value = 42

    engine = mock_database_engine

    with (
        patch(
            "src.database.validate_tables.inspect",
            return_value=mock_inspector,
        ),
        patch.object(engine, "connect") as mock_connect,
        patch.object(engine, "dispose"),
        patch(
            "src.database.validate_tables.get_database_engine",
            return_value=mock_database_engine,
        ),
    ):
        mock_connect.return_value.__enter__.return_value = mock_conn
        assert validate_postgresql_tables() is True


def test_validate_postgresql_tables_missing(mock_database_engine):
    """If a table is missing, validate_postgresql_tables should return False."""
    from src.database.validate_tables import validate_postgresql_tables

    engine = mock_database_engine

    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = [
        "daily_sales",
        "monthly_sales",
    ]

    mock_conn = MagicMock()
    mock_conn.execute.return_value.scalar.return_value = 10

    # Patch the engine methods
    with (
        patch.object(engine, "connect") as mock_connect,
        patch.object(engine, "dispose"),
        patch(
            "src.database.validate_tables.inspect",
            return_value=mock_inspector,
        ),
        patch(
            "src.database.validate_tables.get_database_engine",
            return_value=mock_database_engine,
        ),
    ):
        mock_connect.return_value.__enter__.return_value = mock_conn
        assert validate_postgresql_tables() is False


# ==================================================================
# Gold tables load (load_gold_tables)
# ==================================================================


@patch("src.database.load_gold_tables.FileHandler")
@patch("src.database.load_gold_tables.Path")
def test_load_gold_tables_success(
    mock_path_class, mock_file_handler, mock_database_engine
):
    """load_gold_tables should load parquet files into PostgreSQL."""
    from src.database.load_gold_tables import load_gold_tables

    # Mock path existence: ensure __truediv__ returns self so
    # Path(GOLD_DIR) / file_name propagates the same mock
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = True
    mock_path_instance.__truediv__.return_value = mock_path_instance
    mock_path_class.return_value = mock_path_instance

    # Mock FileHandler.read to return a small DataFrame
    import pandas as pd

    mock_df = pd.DataFrame({"col": [1, 2, 3]})
    mock_file_handler.read.return_value = mock_df

    # Mock to_sql on the DataFrame
    mock_df.to_sql = MagicMock()

    with patch(
        "src.database.load_gold_tables.get_database_engine",
        return_value=mock_database_engine,
    ):
        loaded = load_gold_tables()

    assert len(loaded) > 0
    assert "daily_sales" in loaded


@patch("src.database.load_gold_tables.FileHandler")
@patch("src.database.load_gold_tables.Path")
def test_load_gold_tables_file_not_found(
    mock_path_class, mock_file_handler, mock_database_engine
):
    """load_gold_tables should skip missing parquet files."""
    from src.database.load_gold_tables import load_gold_tables

    # Ensure __truediv__ returns self so derived paths
    # also inherit exists.return_value = False
    mock_path_instance = MagicMock()
    mock_path_instance.exists.return_value = False
    mock_path_instance.__truediv__.return_value = mock_path_instance
    mock_path_class.return_value = mock_path_instance

    with patch(
        "src.database.load_gold_tables.get_database_engine",
        return_value=mock_database_engine,
    ):
        loaded = load_gold_tables()

    assert len(loaded) == 0
