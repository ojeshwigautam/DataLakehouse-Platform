# Spark Gold Pipeline

## Architecture
The Gold layer is produced from the Silver dataset using a Spark-based, modular pipeline:

- `src/spark/gold_pipeline.py`: orchestration, logging, metrics, and writes
- `src/spark/gold_transforms.py`: dataset-specific transformation functions
- `src/spark/gold_validators.py`: dataset validation (schema, row counts, revenue rules, NULL checks)

## Gold datasets
This pipeline generates 7 Parquet datasets under `data/gold/`:

1. `daily_sales.parquet`
2. `monthly_sales.parquet`
3. `seller_performance.parquet`
4. `payment_summary.parquet`
5. `delivery_summary.parquet`
6. `top_products.parquet`
7. `top_states.parquet`

## Business metrics
- Daily Sales: `purchase_date`, `orders`, `revenue`
- Monthly Sales: `month`, `orders`, `revenue`
- Seller Performance: `seller_id`, `orders`, `revenue`, `avg_delivery_days`
- Payment Summary: `payment_type`, `orders`, `total_payment`, `average_payment`
- Delivery Summary: `delivery_status`, `avg_delivery_days`
- Top Products: `product_category`, `orders`, `revenue`
- Top States: `customer_state`, `orders`, `revenue`

## Spark optimizations
- Uses Spark aggregations (`groupBy().agg()`) to keep computation distributed.
- Writes Parquet with `overwrite` mode via `src/spark/writers.py`.

## Execution instructions
Run the Gold pipeline entrypoint:

```bash
python -m src.spark.gold_pipeline
```

Expected console output includes PASS/FAIL per dataset and a final metrics summary.

