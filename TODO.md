# TODO

## DataLakehouse-Platform: Spark Gold Layer

- [x] Create `src/spark/gold_transforms.py` with modular transformation functions.
- [x] Create `src/spark/gold_validators.py` with gold dataset validation logic.
- [x] Extend `src/spark/config.py` with `GOLD_PATH` and all Gold output paths.


- [ ] Create/replace `src/spark/gold_pipeline.py` implementing the Spark Gold pipeline with:
  - reading Silver
  - computing 7 datasets
  - validating each dataset
  - writing each dataset
  - PASS/FAIL console logging + metrics.
- [ ] Add documentation `docs/spark/gold_pipeline.md`.
- [ ] Run tests/regression suite and fix any failures.

