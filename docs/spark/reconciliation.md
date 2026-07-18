# Spark Reconciliation

## Purpose
Validate that the Silver layer output is consistent with the Bronze layer input by generating a JSON reconciliation report.

This ensures:
- Row counts are tracked (and potential removals are surfaced)
- Schema compatibility is checked (missing/extra columns)
- Basic null validation is performed for critical fields
- Duplicate removals are summarized

## Checks performed
1. **Row count comparison**
   - Counts Bronze rows vs Silver rows
   - Computes `rows_removed = bronze_rows - silver_rows`

2. **Schema comparison**
   - Compares column sets between Bronze and Silver
   - Returns:
     - `missing_columns`
     - `extra_columns`
     - `status`: `PASS` if there are no differences

3. **Duplicate summary**
   - If `order_unique_id` exists in Bronze, duplicates are computed as:
     - `sum(count(order_unique_id) - 1)`

4. **Null validation (Silver)**
   - Ensures critical columns are not entirely null in Silver

## Report structure
A reconciliation report is a JSON document with fields like:

```json
{
  "pipeline": "spark_silver",
  "timestamp": "2026-07-18T14:15:00Z",
  "status": "SUCCESS",
  "bronze_rows": 113390,
  "silver_rows": 108640,
  "duplicates_removed": 4750,
  "schema_validation": "PASS",
  "null_validation": "PASS",
  "duration_seconds": 5.8
}
```

## Where the report is saved
Reports are written to:

- `reports/reconciliation/`

Filename format:

- `spark_silver_YYYYMMDD_HHMMSS.json`

## How to run
Run the Spark Silver pipeline:

```bash
python src/spark/silver_pipeline.py
```

After each run, the console prints a reconciliation summary and the saved report path.

