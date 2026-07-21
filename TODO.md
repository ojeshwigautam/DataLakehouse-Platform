# DAG Refactor TODO

- [x] Step 0: Read existing DAG and task files
- [x] Step 1: Create plan and get approval
- [x] Step 2: Remove `run_etl_pipeline` BashOperator
- [x] Step 3: Add 8 new BashOperators:
  - bronze_etl
  - bronze_validation
  - silver_etl
  - silver_validation
  - gold_etl
  - gold_validation
  - postgres_load
  - postgres_validation
- [x] Step 4: Add dependency chain
- [x] Step 5: Verify final file

