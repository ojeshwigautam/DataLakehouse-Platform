# TODO

## Commit 15 - End-to-end pipeline (Silver -> Gold)
- [x] Update `src/pipeline/etl_pipeline.py`
  - [x] Add import `from src.gold.gold_pipeline import create_gold_layer`
  - [x] Change step logs from `STEP 4/4` to `STEP 4/5`
  - [x] Add Step 5 (Gold) logs and call `create_gold_layer()` after Silver
- [x] Test full pipeline by running `python main.py`
- [x] Confirm expected log output includes Silver + Gold steps and `PIPELINE EXECUTED SUCCESSFULLY`


