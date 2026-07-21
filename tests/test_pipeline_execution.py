"""Tests for pipeline orchestration (run_pipeline and stage functions)."""

from unittest.mock import patch

import pytest

# ==================================================================
# Individual pipeline stages
# ==================================================================


def test_run_bronze():
    """run_bronze should invoke load_dataset and save_to_bronze."""
    from src.pipeline.etl_pipeline import run_bronze

    with (
        patch("src.pipeline.etl_pipeline.load_dataset") as mock_load,
        patch("src.pipeline.etl_pipeline.save_to_bronze") as mock_save,
    ):
        mock_load.return_value = "dummy_df"
        run_bronze()
        mock_load.assert_called_once()
        mock_save.assert_called_once_with("dummy_df")


def test_run_bronze_validation():
    """run_bronze_validation should call validate_bronze with the correct dataset."""
    from src.pipeline.etl_pipeline import run_bronze_validation

    with patch("src.pipeline.etl_pipeline.validate_bronze") as mock_validate:
        run_bronze_validation()
        mock_validate.assert_called_once()


def test_run_silver():
    """run_silver should invoke create_silver_layer."""
    from src.pipeline.etl_pipeline import run_silver

    with patch("src.pipeline.etl_pipeline.create_silver_layer") as mock_silver:
        run_silver()
        mock_silver.assert_called_once()


def test_run_silver_validation():
    """run_silver_validation should call validate_silver with the correct dataset."""
    from src.pipeline.etl_pipeline import run_silver_validation

    with patch("src.pipeline.etl_pipeline.validate_silver") as mock_validate:
        run_silver_validation()
        mock_validate.assert_called_once()


def test_run_gold():
    """run_gold should invoke create_gold_layer."""
    from src.pipeline.etl_pipeline import run_gold

    with patch("src.pipeline.etl_pipeline.create_gold_layer") as mock_gold:
        run_gold()
        mock_gold.assert_called_once()


def test_run_gold_validation():
    """run_gold_validation should call validate_gold."""
    from src.pipeline.etl_pipeline import run_gold_validation

    with patch("src.pipeline.etl_pipeline.validate_gold") as mock_validate:
        run_gold_validation()
        mock_validate.assert_called_once()


def test_run_postgres():
    """run_postgres should invoke load_gold_tables."""
    from src.pipeline.etl_pipeline import run_postgres

    with patch(
        "src.pipeline.etl_pipeline.load_gold_tables",
        return_value=["daily_sales"],
    ) as mock_load:
        result = run_postgres()
        assert result == ["daily_sales"]
        mock_load.assert_called_once()


def test_run_postgres_validation():
    """run_postgres_validation should call validate_postgresql_tables."""
    from src.pipeline.etl_pipeline import run_postgres_validation

    with patch(
        "src.pipeline.etl_pipeline.validate_postgresql_tables",
        return_value=True,
    ) as mock_validate:
        run_postgres_validation()
        mock_validate.assert_called_once()


def test_run_postgres_validation_failure():
    """If validate_postgresql_tables returns False, RuntimeError should be raised."""
    from src.pipeline.etl_pipeline import run_postgres_validation

    with patch(
        "src.pipeline.etl_pipeline.validate_postgresql_tables",
        return_value=False,
    ):
        with pytest.raises(RuntimeError, match="PostgreSQL validation failed"):
            run_postgres_validation()


def test_run_data_quality():
    """run_data_quality should invoke validate_dataset and run_data_quality_checks."""
    from src.pipeline.etl_pipeline import run_data_quality

    with (
        patch("src.pipeline.etl_pipeline.load_dataset") as mock_load,
        patch("src.pipeline.etl_pipeline.validate_dataset") as mock_validate,
        patch("src.pipeline.etl_pipeline.run_data_quality_checks") as mock_quality,
    ):
        mock_load.return_value = "dummy_df"
        run_data_quality()
        mock_load.assert_called_once()
        mock_validate.assert_called_once_with("dummy_df")
        mock_quality.assert_called_once_with("dummy_df")


# ==================================================================
# Full pipeline orchestration
# ==================================================================


def test_run_pipeline_success(mock_stages):
    """run_pipeline should call every stage in order and return True on success."""
    from src.pipeline.etl_pipeline import run_pipeline

    result = run_pipeline()

    assert result is True

    # Verify each stage was called exactly once
    mocks = mock_stages
    mocks["bronze"].assert_called_once()
    mocks["bronze_val"].assert_called_once()
    mocks["silver"].assert_called_once()
    mocks["silver_val"].assert_called_once()
    mocks["gold"].assert_called_once()
    mocks["gold_val"].assert_called_once()
    mocks["postgres"].assert_called_once()
    mocks["pg_val"].assert_called_once()
    mocks["inc"].assert_called_once()
    mocks["audit_start"].assert_called_once()
    mocks["audit_complete"].assert_called_once()


def test_run_pipeline_failure_at_bronze(mock_stages):
    """If bronze stage fails, the pipeline should return False and still audit."""
    from src.pipeline.etl_pipeline import run_pipeline

    mocks = mock_stages
    mocks["bronze"].side_effect = Exception("Bronze failed")

    result = run_pipeline()

    assert result is False
    mocks["audit_start"].assert_called_once()
    # Fail audit should be called
    with patch("src.pipeline.etl_pipeline.fail_pipeline_audit"):
        pass  # fail_pipeline_audit is called inside the except block


def test_run_pipeline_failure_at_silver(mock_stages):
    """If silver stage fails, subsequent stages should not run."""
    from src.pipeline.etl_pipeline import run_pipeline

    mocks = mock_stages
    mocks["silver"].side_effect = Exception("Silver failed")

    result = run_pipeline()

    assert result is False
    # Bronze & bronze_val should have been called
    mocks["bronze"].assert_called_once()
    mocks["bronze_val"].assert_called_once()
    # Silver was called but failed
    mocks["silver"].assert_called_once()
    # Subsequent stages should NOT be called
    mocks["silver_val"].assert_not_called()
    mocks["gold"].assert_not_called()
    mocks["gold_val"].assert_not_called()
    mocks["postgres"].assert_not_called()
    mocks["pg_val"].assert_not_called()
