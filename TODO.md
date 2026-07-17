# TODO

## Incremental Bronze → Silver Merge

- [ ] Update `src/processing/silver_pipeline.py`
  - [ ] Modify imports to include `BRONZE_INCREMENTAL_DIR`
  - [ ] Add `load_bronze_data()` above `create_silver_layer()`
  - [ ] Update `create_silver_layer()` to use `load_bronze_data()`
  - [ ] Improve deduplication using `order_unique_id` with `keep="last"`
  - [ ] Improve Silver metrics logging (before/after/duplicates/saved path)
- [ ] Test by running `python -m src.processing.silver_pipeline`
- [ ] Validate logs confirm historical + incremental rows loaded and correct dedup behavior

