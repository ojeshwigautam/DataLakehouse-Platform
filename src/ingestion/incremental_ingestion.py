from pathlib import Path
import shutil

import pandas as pd

from src.config.settings import (
    INCREMENTAL_DATA_DIR,
    BRONZE_INCREMENTAL_DIR,
    PROCESSED_INCREMENTAL_DIR,
)
from src.utils.logger import logger


def get_incremental_files():
    """Find CSV files available for incremental ingestion."""

    files = sorted(INCREMENTAL_DATA_DIR.glob("*.csv"))

    logger.info(
        f"Incremental files discovered : {len(files)}"
    )

    return files


def load_incremental_file(file_path):
    """Load a single incremental CSV file."""

    file_path = Path(file_path)

    logger.info(
        f"Loading incremental file -> {file_path.name}"
    )

    df = pd.read_csv(file_path)

    # Remove unwanted CSV index column if present
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    logger.info(
        f"Incremental rows loaded : {len(df)}"
    )

    return df


def save_incremental_to_bronze(df, source_file):
    """Save incremental data into the Bronze incremental layer."""

    BRONZE_INCREMENTAL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        BRONZE_INCREMENTAL_DIR
        / f"bronze_{source_file.name}"
    )

    df.to_csv(
        output_path,
        index=False,
    )

    logger.info(
        f"Incremental Bronze dataset saved -> {output_path}"
    )

    return output_path


def archive_processed_file(file_path):
    """Move successfully processed incremental files to the processed directory."""

    PROCESSED_INCREMENTAL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        PROCESSED_INCREMENTAL_DIR
        / file_path.name
    )

    # Prevent accidental overwrite of an already processed batch.
    if destination.exists():
        logger.warning(
            f"Batch already archived -> {file_path.name}"
        )

        file_path.unlink()

        return destination

    shutil.move(
        str(file_path),
        str(destination),
    )

    logger.info(
        f"Incremental file archived -> {destination}"
    )

    return destination


def process_incremental_files():
    """Process all available incremental CSV files."""

    logger.info("=" * 60)
    logger.info("INCREMENTAL DATA INGESTION")
    logger.info("=" * 60)

    files = get_incremental_files()

    if not files:
        logger.info(
            "No incremental files found. Nothing to process."
        )
        return []

    processed_files = []

    for file_path in files:

        try:
            # Load incoming batch
            df = load_incremental_file(file_path)

            # Save immutable Bronze copy
            output_path = save_incremental_to_bronze(
                df,
                file_path,
            )

            # Archive source batch only after successful Bronze ingestion
            archive_processed_file(file_path)

            processed_files.append(output_path)

            logger.info(
                f"Incremental batch completed -> {file_path.name}"
            )

        except Exception as error:

            logger.error(
                f"Failed to process {file_path.name}: {error}",
                exc_info=True,
            )

    logger.info("-" * 60)

    logger.info(
        f"Incremental files processed successfully : "
        f"{len(processed_files)}"
    )

    logger.info("=" * 60)

    return processed_files


if __name__ == "__main__":
    process_incremental_files()

