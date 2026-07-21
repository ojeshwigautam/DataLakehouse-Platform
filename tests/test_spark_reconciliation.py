from pyspark.sql import Row

from src.spark.reconciliation import (
    compare_row_counts,
    compare_schema,
    create_reconciliation_report,
    duplicate_summary,
)


def test_compare_row_counts(spark):
    bronze = spark.createDataFrame([Row(a=1), Row(a=2)])
    silver = spark.createDataFrame([Row(a=1)])
    rc = compare_row_counts(bronze, silver)
    assert rc["bronze_rows"] == 2
    assert rc["silver_rows"] == 1
    assert rc["rows_removed"] == 1


def test_compare_schema(spark):
    bronze = spark.createDataFrame([Row(a=1, b=2)])
    silver = spark.createDataFrame([Row(a=1)])
    sc = compare_schema(bronze, silver)
    assert sc["status"] == "FAIL"
    assert "b" in sc["missing_columns"]
    assert sc["extra_columns"] == []


def test_duplicate_summary_counts_duplicates(spark):
    bronze = spark.createDataFrame(
        [
            Row(order_unique_id="o1"),
            Row(order_unique_id="o1"),
            Row(order_unique_id="o2"),
        ]
    )
    # silver removes duplicates by order_unique_id
    silver = spark.createDataFrame(
        [
            Row(order_unique_id="o1"),
            Row(order_unique_id="o2"),
        ]
    )

    dup = duplicate_summary(bronze, silver)
    assert dup["duplicates_removed"] == 1


def test_create_reconciliation_report_schema_and_keys(spark):
    bronze = spark.createDataFrame(
        [
            Row(
                order_unique_id="o1",
                order_purchase_timestamp="2026-01-01",
                price=10.0,
                payment_value=11.0,
                freight_value=1.0,
            ),
            Row(
                order_unique_id="o2",
                order_purchase_timestamp="2026-01-02",
                price=20.0,
                payment_value=21.0,
                freight_value=2.0,
            ),
        ]
    )
    silver = spark.createDataFrame(
        [
            Row(
                order_unique_id="o1",
                order_purchase_timestamp="2026-01-01",
                price=10.0,
                payment_value=11.0,
                freight_value=1.0,
            ),
        ]
    )

    report = create_reconciliation_report(
        bronze_df=bronze,
        silver_df=silver,
        pipeline="spark_silver",
        duration=1.234,
    )

    assert report["pipeline"] == "spark_silver"
    assert report["bronze_rows"] == 2
    assert report["silver_rows"] == 1
    assert "schema_validation" in report
    assert "null_validation" in report
    assert isinstance(report["duration_seconds"], float)
