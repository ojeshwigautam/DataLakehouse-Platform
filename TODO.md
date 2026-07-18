- [ ] Expand `src/spark/config.py` to centralize PROJECT_ROOT, BRONZE_PATH, SILVER_PATH, APP_NAME, SHUFFLE_PARTITIONS, PARQUET_COMPRESSION
- [ ] Update `src/spark/session.py` to configure Spark with AQE, shuffle partitions, parquet compression
- [ ] Implement `clean_orders(df)` in `src/spark/transforms.py`
- [ ] Implement Spark DataFrame validations in `src/spark/validators.py`
- [ ] Refactor `src/spark/silver_pipeline.py` into an orchestrator (logging, metrics, read/transform/validate/write)
- [ ] Create `docs/spark/silver_pipeline.md`
- [ ] Run tests / smoke checks (`pytest -q`, and/or `python scripts/test_spark.py`)

