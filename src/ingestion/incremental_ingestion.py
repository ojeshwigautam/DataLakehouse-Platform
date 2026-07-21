"""
Legacy incremental ingestion module.

**Deprecated** — This module is retained for backward compatibility.
New code should use :class:`~src.ingestion.incremental_loader.IncrementalLoader`
directly.

The legacy ``process_incremental_files()`` function now delegates to
the new checksum-based :class:`IncrementalLoader` and logs a
deprecation warning.
"""

import warnings
from pathlib import Path
from typing import List, Union

import pandas as pd

from src.config.settings import INCREMENTAL_DATA_DIR, PROCESSED_INCREMENTAL_DIR
from src.ingestion.incremental_loader import IncrementalLoader
from src.utils.logger import logger


def get_incremental_files() -> List[Path]:
    """Find incremental batch parquet files available for ingestion.

    .. deprecated::
        Use :meth:`IncrementalLoader.get_new_files` instead.
    """
    warnings.warn(
        "get_incremental_files() is deprecated. "
        "Use IncrementalLoader.get_new_files() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    files = sorted(INCREMENTAL_DATA_DIR.glob("*.parquet"))

    logger.info(f"Incremental files discovered : {len(files)}")

    return files


def load_incremental_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load a single incremental Parquet file.

    .. deprecated::
        Use ``IncrementalLoader.load_new_files([path])`` instead.
    """
    warnings.warn(
        "load_incremental_file() is deprecated. "
        "Use IncrementalLoader.load_new_files() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    file_path = Path(file_path)

    logger.info(f"Loading incremental file -> {file_path.name}")

    df = pd.read_parquet(file_path)

    # Remove unwanted parquet index column if present (legacy batches)
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    logger.info(f"Incremental rows loaded : {len(df)}")

    return df


def save_incremental_to_bronze(
    df: pd.DataFrame,
    source_file: Path,
) -> Path:
    """Save incremental data into the Bronze incremental layer.

    .. deprecated::
        Use ``IncrementalLoader.merge_incremental(df)`` instead.
    """
    warnings.warn(
        "save_incremental_to_bronze() is deprecated. "
        "Use IncrementalLoader.merge_incremental() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    from src.config.settings import BRONZE_INCREMENTAL_DIR

    BRONZE_INCREMENTAL_DIR.mkdir(parents=True, exist_ok=True)

    # Write a stable parquet filename based on source stem
    output_path = BRONZE_INCREMENTAL_DIR / f"bronze_{source_file.stem}.parquet"

    df.to_parquet(output_path, index=False)

    logger.info(f"Incremental Bronze dataset saved -> {output_path}")

    return output_path


def archive_processed_file(file_path: Path) -> Path:
    """Move successfully processed incremental files to the processed directory.

    .. deprecated::
        The new incremental loader does **not** move files.  It detects
        duplicates via checksum, so archiving is unnecessary.
    """
    warnings.warn(
        "archive_processed_file() is deprecated. "
        "The new checksum-based incremental loader does not require "
        "file archiving.",
        DeprecationWarning,
        stacklevel=2,
    )

    import shutil

    PROCESSED_INCREMENTAL_DIR.mkdir(parents=True, exist_ok=True)

    destination = PROCESSED_INCREMENTAL_DIR / file_path.name

    # Prevent accidental overwrite of an already processed batch.
    if destination.exists():
        logger.warning(f"Batch already archived -> {file_path.name}")
        file_path.unlink()
        return destination

    shutil.move(str(file_path), str(destination))

    logger.info(f"Incremental file archived -> {destination}")

    return destination


def process_incremental_files() -> List[Path]:
    """Process all available incremental files using checksum dedup.

    .. deprecated::
        Use :meth:`IncrementalLoader.run()` directly.

    This function wraps the new ``IncrementalLoader`` to maintain
    backward compatibility with :mod:`src.pipeline.etl_pipeline`.
    """
    warnings.warn(
        "process_incremental_files() is deprecated. "
        "Use IncrementalLoader.run() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    logger.info("=" * 60)
    logger.info("INCREMENTAL DATA INGESTION (legacy wrapper → checksum-based)")
    logger.info("=" * 60)

    loader = IncrementalLoader()
    result = loader.run()

    if result.status == "SUCCESS" and result.bronze_path:
        return [result.bronze_path]

    return []


if __name__ == "__main__":
    process_incremental_files()
