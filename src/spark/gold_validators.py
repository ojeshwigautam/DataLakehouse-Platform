"""Gold layer validation utilities."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def validate_gold_dataset(
    df: DataFrame,
    *,
    required_columns: list[str],
    revenue_column: str | None = "revenue",
    dimension_columns: list[str] | None = None,
) -> None:
    """Raise ValueError if validation fails."""

    row_count = df.count()
    if row_count <= 0:
        raise ValueError("Gold dataset validation failed: row count must be > 0")

    df_columns = set(df.columns)
    missing = [c for c in required_columns if c not in df_columns]
    if missing:
        raise ValueError(
            f"Gold dataset validation failed: missing required columns: {missing}"
        )

    if revenue_column and revenue_column in df_columns:
        neg_revenue = df.filter(F.col(revenue_column) < 0).limit(1).count()
        if neg_revenue > 0:
            raise ValueError("Gold dataset validation failed: revenue must be >= 0")

    if dimension_columns:
        for c in dimension_columns:
            if c not in df_columns:
                continue
            nulls = df.filter(F.col(c).isNull()).limit(1).count()
            if nulls > 0:
                raise ValueError(
                    f"Gold dataset validation failed: dimension '{c}' contains NULL"
                )
