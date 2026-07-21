"""
Checksum Generator — Prevents duplicate processing even if filenames change.

Provides functions to compute file hashes using SHA-256 or MD5,
and a convenience method that integrates with the existing
:class:`src.metadata.file_tracker.FileTracker` for persistence.

Usage::

    from src.ingestion.checksum import calculate_sha256, compare_checksum

    checksum = calculate_sha256("/data/file.csv")
    is_dup   = compare_checksum("/data/file.csv", stored_checksum)
"""

import hashlib
from pathlib import Path
from typing import Union


def _digest(
    file_path: Union[str, Path],
    algorithm: str,
    chunk_size: int = 65536,
) -> str:
    """Compute the hex digest of *file_path* using *algorithm*.

    Reads the file in *chunk_size* byte blocks to handle large files
    without loading the entire content into memory.
    """
    hasher = hashlib.new(algorithm)
    path = Path(file_path)

    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()


# ── Public API ─────────────────────────────────────────────────────


def calculate_sha256(
    file_path: Union[str, Path],
    chunk_size: int = 65536,
) -> str:
    """Compute the SHA-256 hex digest of a file.

    Parameters
    ----------
    file_path : str or Path
        Path to the file.
    chunk_size : int
        Read buffer size in bytes (default 64 KiB).

    Returns
    -------
    str
        64-character hexadecimal SHA-256 checksum.
    """
    return _digest(file_path, "sha256", chunk_size)


def calculate_md5(
    file_path: Union[str, Path],
    chunk_size: int = 65536,
) -> str:
    """Compute the MD5 hex digest of a file.

    .. note::

        MD5 is provided for legacy interop.  SHA-256 is the recommended
        default for duplicate detection.

    Parameters
    ----------
    file_path : str or Path
        Path to the file.
    chunk_size : int
        Read buffer size in bytes (default 64 KiB).

    Returns
    -------
    str
        32-character hexadecimal MD5 checksum.
    """
    return _digest(file_path, "md5", chunk_size)


def compare_checksum(
    file_path: Union[str, Path],
    stored_checksum: str,
    algorithm: str = "sha256",
) -> bool:
    """Compare a file's current checksum against a stored value.

    Parameters
    ----------
    file_path : str or Path
        Path to the file.
    stored_checksum : str
        Previously computed checksum to compare against.
    algorithm : str
        Hash algorithm to use (``"sha256"`` or ``"md5"``).

    Returns
    -------
    bool
        ``True`` if the checksums match, ``False`` otherwise.
    """
    current = _digest(file_path, algorithm)
    return current == stored_checksum
