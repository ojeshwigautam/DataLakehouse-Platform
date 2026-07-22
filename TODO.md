# Fix: FileTracker Double-Insert Bug

## Status: ✅ ALL STEPS COMPLETE

### 1. Fix `src/metadata/file_tracker.py` ✅
- [x] Remove `self.mark_processed(file_name, file_path, run_id)` from `prevent_duplicate()`
- [x] Remove `run_id` parameter from `prevent_duplicate()` signature
- [x] Update docstring for `prevent_duplicate()`

### 2. Fix `src/ingestion/incremental_loader.py` ✅
- [x] Update `_filter_new_files()` caller to not pass `run_id` to `prevent_duplicate()`
- [x] Remove redundant `calculate_sha256(fp)` in `run()` before `mark_processed()`
- [x] Update `get_new_files()` caller to not pass `run_id` to `prevent_duplicate()`

### 3. Fix `tests/test_file_tracker.py` ✅
- [x] Update `test_prevent_duplicate_returns_false_first_time` — remove `run_id`, verify `mark_processed` NOT called
- [x] Update `test_prevent_duplicate_returns_true_for_duplicate` — remove `run_id`

### 4. Fix `tests/test_incremental_loader.py` ✅
- [x] Update `test_partial_duplicates` mock signature to match new `prevent_duplicate(file_path)`
- [x] Update `test_update_metadata` to pre-initialise lazy components

### 5. Run tests ✅
- [x] All 18 tests passing (`test_file_tracker.py` + `test_incremental_loader.py`)

