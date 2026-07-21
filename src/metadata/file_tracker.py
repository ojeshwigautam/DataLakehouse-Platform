"""
FileTracker — Checksum-based duplicate file detection.

Computes SHA-256 checksums for files and checks the metadata
database to prevent duplicate processing.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

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
        """
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
        """
        checksum = self.compute_checksum(file_path)

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
        run_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """Check if a file has already been processed; if not,
        compute its checksum and record it.

        Args:
            file_path: Path to the file to process.
            run_id:    The current pipeline run ID.

        Returns:
            (was_already_processed, checksum_or_None)
        """
        file_name = file_path.name
        checksum = self.compute_checksum(file_path)

        if self.is_processed(file_name, checksum):
            logger.info(f"Skipping duplicate file | file={file_name}")
            return True, checksum

        self.mark_processed(file_name, file_path, run_id)
        return False, checksum
