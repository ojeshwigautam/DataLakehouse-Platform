"""
Incremental Loader — Orchestrates the end-to-end incremental ingestion flow.

Flow
----
1. **Discover** files in the incremental folder.
2. **Compare** file checksums against the metadata database.
3. **Load** only files that have not been processed before.
4. **Append** the new data to the existing Bronze layer.
5. **Update** metadata (processed_files + watermarks).

This component reuses the existing :class:`FileTracker` for duplicate
detection and :class:`MetadataManager` for watermark tracking.

Usage::

    from src.ingestion.incremental_loader import IncrementalLoader

    loader = IncrementalLoader()
    result = loader.run()

    if result.new_files_count > 0:
        print(f"Loaded {result.rows_loaded} rows from {result.new_files_count} file(s)")
    else:
        print("No new files to process.")
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from src.config.settings import BRONZE_INCREMENTAL_DIR, INCREMENTAL_DATA_DIR
from src.ingestion.checksum import calculate_sha256
from src.ingestion.file_discovery import FileDiscoverer
from src.metadata.file_tracker import FileTracker
from src.metadata.metadata_manager import MetadataManager
from src.storage.file_handler import FileHandler
from src.utils.decorators import handle_exceptions, log_execution, measure_time
from src.utils.logger import logger

# ── Result container ───────────────────────────────────────────────


@dataclass
class IncrementalResult:
    """Summary of an incremental ingestion run."""

    total_files_discovered: int = 0
    already_processed: int = 0
    new_files: List[Path] = field(default_factory=list)
    new_files_count: int = 0
    rows_loaded: int = 0
    bronze_path: Optional[Path] = None
    execution_time_seconds: float = 0.0
    status: str = "SUCCESS"


# ── Incremental Loader ─────────────────────────────────────────────


class IncrementalLoader:
    """Orchestrate the incremental ingestion pipeline.

    Parameters
    ----------
    incremental_dir : str or Path, optional
        Directory containing incremental files. Defaults to settings value.
    bronze_dir : str or Path, optional
        Directory to write/append bronze data. Defaults to settings value.
    run_id : str, optional
        Pipeline run ID for metadata tracking. Auto-generated if not provided.
    """

    def __init__(
        self,
        incremental_dir: Optional[Union[str, Path]] = None,
        bronze_dir: Optional[Union[str, Path]] = None,
        run_id: Optional[str] = None,
    ):
        self.incremental_dir = Path(incremental_dir or INCREMENTAL_DATA_DIR)
        self.bronze_dir = Path(bronze_dir or BRONZE_INCREMENTAL_DIR)
        self._run_id = run_id

        self._discoverer = FileDiscoverer(base_path=self.incremental_dir)
        self._file_tracker = FileTracker()
        self._metadata_mgr = MetadataManager()

    # ── Public entry point ─────────────────────────────────────────

    @log_execution
    @measure_time
    @handle_exceptions
    def run(
        self,
        run_id: Optional[str] = None,
    ) -> IncrementalResult:
        """Execute the full incremental ingestion workflow.

        Parameters
        ----------
        run_id : str, optional
            Override the run ID for this execution.

        Returns
        -------
        IncrementalResult
            Summary of what was processed.
        """
        import time

        start_time = time.time()
        result = IncrementalResult()

        effective_run_id = run_id or self._run_id or "manual-run"

        logger.info("=" * 60)
        logger.info("INCREMENTAL LOADER (Checksum-based)")
        logger.info("=" * 60)

        # 1. Discover
        all_files = self._discoverer.discover_files()
        result.total_files_discovered = len(all_files)
        logger.info(f"Incremental Folder : {len(all_files)} file(s)")

        # 2. Filter new files
        new_files = self._filter_new_files(all_files)
        result.new_files = new_files
        result.new_files_count = len(new_files)
        result.already_processed = len(all_files) - len(new_files)

        logger.info(f"Already Processed : {result.already_processed}")
        logger.info(f"New Files         : {result.new_files_count}")

        if not new_files:
            logger.info("No new files to process. Skipping.")
            result.execution_time_seconds = time.time() - start_time
            return result

        # 3. Load and merge
        try:
            df_combined = self._load_and_merge(new_files)
            result.rows_loaded = len(df_combined)

            logger.info(f"Rows Loaded       : {result.rows_loaded}")

            # 4. Save to bronze
            result.bronze_path = self._save_to_bronze(df_combined)

            # 5. Update metadata (mark all new files as processed)
            for fp in new_files:
                calculate_sha256(fp)
                self._file_tracker.mark_processed(
                    file_name=fp.name,
                    file_path=fp,
                    run_id=effective_run_id,
                    status="SUCCESS",
                )

            # 6. Update watermark
            latest_file = new_files[-1] if new_files else None
            if latest_file:
                self._metadata_mgr.update_watermark(
                    pipeline_name="incremental_loader",
                    last_processed_file=latest_file.name,
                    last_processed_timestamp=datetime.now(),
                )

            logger.info("Bronze Updated    : √")
            logger.info("Metadata Updated  : √")

        except Exception as exc:
            result.status = "FAILED"
            logger.error(f"Incremental load failed: {exc}", exc_info=True)
            raise

        finally:
            result.execution_time_seconds = time.time() - start_time
            logger.info("-" * 60)
            logger.info(f"Execution Time    : {result.execution_time_seconds:.2f} sec")
            logger.info(f"Status            : {result.status}")
            logger.info("=" * 60)

        return result

    # ── Internal helpers ───────────────────────────────────────────

    def _filter_new_files(
        self,
        files: List[Path],
    ) -> List[Path]:
        """Return only files that have NOT been processed before.

        Uses the ``FileTracker.prevent_duplicate()`` which checks both
        filename and checksum.  If a file has the same name but different
        content (or same content but different name) it is still skipped
        when the checksum matches a previously-processed record.
        """
        new_files: List[Path] = []

        for fp in files:
            was_processed, _ = self._file_tracker.prevent_duplicate(
                file_path=fp,
                run_id=self._run_id or "discovery-pass",
            )

            if not was_processed:
                new_files.append(fp)
            else:
                logger.info(f"Skipping (already processed): {fp.name}")

        return new_files

    def _load_and_merge(
        self,
        new_files: List[Path],
    ) -> pd.DataFrame:
        """Load all *new_files* and append to the existing bronze data.

        If bronze already exists for incremental data, the existing
        parquet is read first and new data is appended.
        """
        # Load existing bronze data if present
        existing_bronze = self._read_existing_bronze()

        # Load new files
        new_dfs: List[pd.DataFrame] = []
        for fp in new_files:
            logger.info(f"Reading : {fp.name}")
            df = FileHandler.read(fp)
            new_dfs.append(df)

        df_new = pd.concat(new_dfs, ignore_index=True)

        # Merge: append new data to existing
        if existing_bronze is not None and not existing_bronze.empty:
            combined = pd.concat([existing_bronze, df_new], ignore_index=True)
            logger.info(
                f"Merged incremental → Bronze "
                f"(existing={len(existing_bronze)}, "
                f"new={len(df_new)}, "
                f"total={len(combined)})"
            )
        else:
            combined = df_new
            logger.info(f"Fresh bronze layer created " f"(rows={len(combined)})")

        return combined

    def _read_existing_bronze(self) -> Optional[pd.DataFrame]:
        """Read the existing incremental bronze parquet if it exists."""
        bronze_parquet = self.bronze_dir / "bronze_incremental.parquet"

        if bronze_parquet.exists():
            logger.info(f"Reading existing bronze: {bronze_parquet}")
            return FileHandler.read(bronze_parquet)

        return None

    def _save_to_bronze(
        self,
        df: pd.DataFrame,
    ) -> Path:
        """Write the merged DataFrame to the bronze incremental layer."""
        self.bronze_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.bronze_dir / "bronze_incremental.parquet"

        df.to_parquet(output_path, index=False)

        logger.info(f"Bronze incremental saved → {output_path} " f"({len(df)} rows)")
        return output_path

    # ── Public helpers ─────────────────────────────────────────────

    def get_new_files(
        self,
        run_id: Optional[str] = None,
    ) -> List[Path]:
        """Discover and return only new (unprocessed) file paths.

        This is a lighter-weight alternative to ``run()`` when you only
        need to know *which* files would be processed, without loading
        them.
        """
        all_files = self._discoverer.discover_files()
        return self._filter_new_files(all_files)

    def load_new_files(
        self,
        new_files: List[Path],
    ) -> pd.DataFrame:
        """Load the provided list of new files into a single DataFrame.

        Parameters
        ----------
        new_files : List[Path]
            File paths to load.

        Returns
        -------
        pd.DataFrame
            Concatenated data from all files.
        """
        return self._load_and_merge(new_files)

    def merge_incremental(
        self,
        df_new: pd.DataFrame,
    ) -> Path:
        """Append *df_new* to the existing bronze layer.

        Parameters
        ----------
        df_new : pd.DataFrame
            New data to append.

        Returns
        -------
        Path
            Path of the updated bronze parquet file.
        """
        combined = self._load_and_merge_from_dfs([df_new])
        return self._save_to_bronze(combined)

    def update_metadata(
        self,
        file_paths: List[Path],
        run_id: str,
        status: str = "SUCCESS",
    ):
        """Mark a list of files as processed and update the watermark.

        Parameters
        ----------
        file_paths : List[Path]
            Files to mark as processed.
        run_id : str
            Pipeline run identifier.
        status : str
            Processing status (``"SUCCESS"`` or ``"FAILED"``).
        """
        for fp in file_paths:
            calculate_sha256(fp)
            self._file_tracker.mark_processed(
                file_name=fp.name,
                file_path=fp,
                run_id=run_id,
                status=status,
            )

        latest_file = file_paths[-1] if file_paths else None
        if latest_file:
            self._metadata_mgr.update_watermark(
                pipeline_name="incremental_loader",
                last_processed_file=latest_file.name,
                last_processed_timestamp=datetime.now(),
            )

    def _load_and_merge_from_dfs(
        self,
        new_dfs: List[pd.DataFrame],
    ) -> pd.DataFrame:
        """Merge a list of new DataFrames with existing bronze."""
        existing_bronze = self._read_existing_bronze()

        df_new = pd.concat(new_dfs, ignore_index=True)

        if existing_bronze is not None and not existing_bronze.empty:
            combined = pd.concat([existing_bronze, df_new], ignore_index=True)
        else:
            combined = df_new

        return combined
