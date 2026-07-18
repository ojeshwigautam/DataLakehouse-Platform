"""Spark reconciliation helpers.

Compares Bronze vs Silver DataFrames for:
- Row counts
- Schema differences
- Duplicate summaries

This module is intentionally Spark-native (except where we only inspect
schema/column metadata).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


_CRITICAL_NULL_COLUMNS: List[str] = [
    "order_unique_id",
    "order_purchase_timestamp",
    "price",
    "payment_value",
    "freight_value",
]


def compare_row_counts(bronze_df: DataFrame, silver_df: DataFrame) -> Dict[str, int]:
    """Compare row counts between Bronze and Silver.

    Returns:
        {
          "bronze_rows": ...,
          "silver_rows": ...,
          "rows_removed": ...,
        }
    """

    bronze_rows = int(bronze_df.count())
    silver_rows = int(silver_df.count())
    rows_removed = bronze_rows - silver_rows
    return {
        "bronze_rows": bronze_rows,
        "silver_rows": silver_rows,
        "rows_removed": rows_removed,
    }


def compare_schema(bronze_df: DataFrame, silver_df: DataFrame) -> Dict[str, Any]:
    """Compare schema (column presence) between Bronze and Silver.

    Returns:
        {
          "missing_columns": [...],
          "extra_columns": [...],
          "status": "PASS" | "FAIL",
        }
    """

    bronze_cols = set(bronze_df.columns)
    silver_cols = set(silver_df.columns)

    missing_columns = sorted(list(bronze_cols - silver_cols))
    extra_columns = sorted(list(silver_cols - bronze_cols))

    status = "PASS" if not missing_columns and not extra_columns else "FAIL"

    return {
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "status": status,
    }


def _count_duplicate_orders(df: DataFrame, order_unique_id_col: str = "order_unique_id") -> int:
    if df is None or order_unique_id_col not in df.columns:
        return 0

    # Count duplicates by summing (count-1) per key.
    # Example: if order appears 3 times -> duplicates removed count contributes 2.
    dup_summary = (
        df.groupBy(order_unique_id_col)
        .count()
        .withColumn("dup_minus_one", F.col("count") - F.lit(1))
        .filter(F.col("dup_minus_one") > 0)
        .select(F.sum(F.col("dup_minus_one")).alias("dup_removed"))
        .collect()
    )

    return int(dup_summary[0]["dup_removed"] or 0) if dup_summary else 0


def duplicate_summary(bronze_df: DataFrame, silver_df: DataFrame) -> Dict[str, int]:
    """Summarize how many duplicates were removed.

    Primary method:
    - If `order_unique_id` exists in Bronze: compute duplicates as sum(count-1).

    Fallback method:
    - If the above isn't possible: use rows_removed from row counts.

    Returns:
        {"duplicates_removed": ...}
    """

    duplicates_removed = _count_duplicate_orders(bronze_df, "order_unique_id")
    if duplicates_removed > 0:
        return {"duplicates_removed": int(duplicates_removed)}

    # fallback (can be negative if Silver > Bronze)
    rc = compare_row_counts(bronze_df, silver_df)
    return {"duplicates_removed": int(max(rc["rows_removed"], 0))}


def _null_validation(silver_df: DataFrame) -> str:
    """Return PASS if critical columns are not entirely null in Silver."""

    input_count = int(silver_df.count())
    if input_count <= 0:
        return "FAIL"

    for col_name in _CRITICAL_NULL_COLUMNS:
        if col_name not in silver_df.columns:
            return "FAIL"

        field = next((f for f in silver_df.schema.fields if f.name == col_name), None)
        if field is None:
            return "FAIL"

        # Handle NaN for floating-like types.
        if field.dataType.simpleString() in {"double", "float"}:
            missing = silver_df.filter(F.col(col_name).isNull() | F.isnan(F.col(col_name))).count()
        else:
            missing = silver_df.filter(F.col(col_name).isNull()).count()

        if missing >= input_count:
            return "FAIL"

    return "PASS"


def create_reconciliation_report(
    bronze_df: DataFrame,
    silver_df: DataFrame,
    pipeline: str,
    duration: float,
    *,
    status: str = "SUCCESS",
    timestamp: str | None = None,
) -> Dict[str, Any]:
    """Create the JSON-serializable reconciliation report."""

    if timestamp is None:
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    rc = compare_row_counts(bronze_df, silver_df)
    sc = compare_schema(bronze_df, silver_df)
    dup = duplicate_summary(bronze_df, silver_df)
    null_val = _null_validation(silver_df)

    schema_validation = sc["status"]

    return {
        "pipeline": pipeline,
        "timestamp": timestamp,
        "status": status,
        "bronze_rows": rc["bronze_rows"],
        "silver_rows": rc["silver_rows"],
        "duplicates_removed": dup["duplicates_removed"],
        "schema_validation": schema_validation,
        "null_validation": null_val,
        "duration_seconds": round(float(duration), 3),
    }

