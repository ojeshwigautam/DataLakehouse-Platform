# Pipeline Refactoring TODO ✅

## Goal
Refactor `src/pipeline/etl_pipeline.py` into a clean, modular pipeline with dedicated stage functions.

## Steps

### Step 1: Create stage helper functions
- [x] `run_bronze(df)` — STEP 2/8 → calls `save_to_bronze(df)`
- [x] `run_bronze_validation()` — STEP 3/8 → calls `validate_bronze(BRONZE_DATASET)`
- [x] `run_silver()` — STEP 4/8 → calls `create_silver_layer()`
- [x] `run_silver_validation()` — STEP 5/8 → calls `validate_silver(SILVER_DATASET)`
- [x] `run_gold()` — STEP 6/8 → calls `create_gold_layer()`
- [x] `run_gold_validation()` — STEP 7/8 → calls `validate_gold()`
- [x] `run_postgres()` — STEP 8/8 → calls `load_gold_tables()`, returns `tables`
- [x] `run_postgres_validation()` — STEP 9/9 → calls `validate_postgresql_tables()`
- [x] `run_data_quality(df)` — runs `validate_dataset(df)` and `run_data_quality_checks(df)` (preserved as a stage)

### Step 2: Rewrite `run_pipeline()` body
- [x] Clean orchestration using the stage functions
- [x] Keep pipeline audit (start, complete, fail)
- [x] Keep summary logging at the end
- [x] Remove old inline step logic

### Step 3: Update imports
- [x] Add imports for: `validate_bronze`, `validate_silver`, `validate_gold`, `validate_postgresql_tables`
- [x] Keep imports for: `load_dataset`, `save_to_bronze`, `create_silver_layer`, `create_gold_layer`, `load_gold_tables`
- [x] Keep imports for: `validate_dataset`, `run_data_quality_checks`
- [x] Keep imports for: pipeline audit functions
- [x] Remove unused imports

### Step 4: Verify
- [x] Syntax check: `python -c "from src.pipeline.etl_pipeline import run_pipeline"` ✅
- [ ] Run any existing pipeline tests

