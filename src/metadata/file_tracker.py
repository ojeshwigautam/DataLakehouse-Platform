"""
FileTracker — Checksum-based duplicate file detection.

Computes SHA-256 checksums for files and checks the metadata
database to prevent duplicate processing.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session

from src.database.connection import get_database_engine
from src.metadata.metadata_models import ProcessedFile
from src.utils.logger import logger


class FileTracker:
    """Track processed files and prevent duplicate processing."""

    def __init__(self):
        self.engine = get_database_engine()
        self._hash_algorithm = "sha256"

    # ----------------------------------------------------------
    # Checksum Computation
    # ----------------------------------------------------------

    def compute_checksum(
        self,
        file_path: Path,
        chunk_size: int = 65536,
    ) -> str:
        """Compute the SHA-256 hex digest of a file.

        Reads the file in chunks to handle large files without
        loading the entire contents into memory.
        """
        hasher = hashlib.sha256()

        with open(file_path, "rb") as fh:
            while True:
                chunk = fh.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)

        checksum = hasher.hexdigest()
        logger.debug(
            f"Checksum computed | file={file_path.name} | "
            f"checksum={checksum[:16]}..."
        )
        return checksum

    # ----------------------------------------------------------
    # Duplicate Check
    # ----------------------------------------------------------

    def is_processed(
        self,
        file_name: str,
        checksum: str,
    ) -> bool:
        """Check whether a file (name + checksum) has already been
        processed successfully.

        Returns True if a record exists with status='SUCCESS'.
        Raises sqlalchemy_exc.OperationalError on DB connectivity issues.
        """
        try:
            with Session(self.engine) as session:
                exists = (
                    session.query(ProcessedFile)
                    .filter_by(
                        file_name=file_name,
                        checksum=checksum,
                        status="SUCCESS",
                    )
                    .first()
                )
        except sqlalchemy_exc.OperationalError as error:
            logger.error(
                f"DB connectivity error in is_processed("
                f"file_name={file_name}): {error}"
            )
            raise

        if exists:
            logger.info(
                f"File already processed | file={file_name} | "
                f"checksum={checksum[:16]}..."
            )
            return True

        return False

    # ----------------------------------------------------------
    # Mark Processed
    # ----------------------------------------------------------

    def mark_processed(
        self,
        file_name: str,
        file_path: Path,
        run_id: str,
        status: str = "SUCCESS",
    ) -> str:
        """Compute the file's checksum and record it as processed.

        Returns the computed checksum string.
        Raises sqlalchemy_exc.OperationalError on DB connectivity issues.
        """
        checksum = self.compute_checksum(file_path)

        try:
            with Session(self.engine) as session:
                record = ProcessedFile(
                    file_name=file_name,
                    checksum=checksum,
                    processed_timestamp=datetime.now(),
                    run_id=run_id,
                    status=status,
                )
                session.add(record)
                session.commit()
        except sqlalchemy_exc.OperationalError as error:
            logger.error(
                f"DB connectivity error in mark_processed("
                f"file_name={file_name}): {error}"
            )
            raise

        logger.info(
            f"File marked processed | file={file_name} | "
            f"checksum={checksum[:16]}... | run_id={run_id}"
        )
        return checksum

    # ----------------------------------------------------------
    # Combined Check-And-Mark (prevent duplicate)
    # ----------------------------------------------------------

    def prevent_duplicate(
        self,
        file_path: Path,
    ) -> Tuple[bool, Optional[str]]:
        """Check if a file has already been processed.

        This method only **checks** for duplicates — it does NOT
        mark the file as processed. The caller is responsible for
        calling :meth:`mark_processed` only after the file has been
        successfully loaded (Bronze write), ensuring that a failed
        load does not record a false-positive processed file.

        Args:
            file_path: Path to the file to check.

        Returns:
            (was_already_processed, checksum_or_None)
        """
        file_name = file_path.name
        checksum = self.compute_checksum(file_path)

        try:
            if self.is_processed(file_name, checksum):
                logger.info(f"Skipping duplicate file | file={file_name}")
                return True, checksum

            # DO NOT mark here.
            # The caller will mark the file only after successful processing.
            return False, checksum

        except sqlalchemy_exc.OperationalError as error:
            logger.error(
                f"Database unavailable for prevent_duplicate("
                f"file={file_name}). Treating as unprocessed. "
                f"Error: {error}"
            )
            # When DB is unreachable, we return (False, checksum) to
            # allow the pipeline to proceed with processing. The file
            # will be re-evaluated on the next run when DB is back.
            return False, checksum
