# TODO - CSV to Parquet Migration

- [x] Update `src/config/settings.py` dataset constants to use `.parquet` (keep `RAW_DATASET` as `.csv`).
- [x] Update `src/bronze/save_to_bronze.py` to write `bronze_orders.parquet`.
- [x] Update `src/ingestion/incremental_ingestion.py` to discover `*.parquet`, write batches as parquet, and archive accordingly.
- [x] Update `src/processing/silver_pipeline.py` to discover incremental bronze `*.parquet` and output `silver_orders.parquet`.
- [x] Update `src/database/load_gold_tables.py` `GOLD_TABLES` keys to use `*.parquet` filenames.
- [x] Run pipeline via `python main.py`.
- [ ] Run tests (`pytest -q`) if available/expected by repo.


