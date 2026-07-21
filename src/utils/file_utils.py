"""
File utility functions for the Data Lakehouse Platform.

Provides helpers for file extension extraction, hidden/temp file
detection, and directory management used across the ingestion layer.
"""

from pathlib import Path
from typing import Set, Union

# ── Supported file formats ─────────────────────────────────────────

SUPPORTED_EXTENSIONS: Set[str] = {".csv", ".parquet", ".pq", ".json"}


# ── Public helpers ─────────────────────────────────────────────────


def get_file_extension(path: Union[str, Path]) -> str:
    """Return the lowercased file extension (e.g. ``.csv``).

    Parameters
    ----------
    path : str or Path
        File path to inspect.

    Returns
    -------
    str
        Lowercased extension including the dot, or ``""`` if none.
    """
    return Path(path).suffix.lower()


def is_supported_format(path: Union[str, Path]) -> bool:
    """Return *True* if the file extension is a supported format.

    Currently supported: ``.csv``, ``.parquet``, ``.pq``, ``.json``.
    """
    return get_file_extension(path) in SUPPORTED_EXTENSIONS


def is_hidden_file(path: Union[str, Path]) -> bool:
    """Return *True* if the file is considered hidden.

    On Windows this checks the FILE_ATTRIBUTE_HIDDEN flag;
    on all platforms a leading dot is also treated as hidden.
    """
    p = Path(path)
    if p.name.startswith("."):
        return True
    try:
        import stat

        attrs = p.stat().st_file_attributes  # type: ignore[attr-defined]
        return bool(attrs & stat.FILE_ATTRIBUTE_HIDDEN)  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return False


def is_temp_file(path: Union[str, Path]) -> bool:
    """Return *True* if the filename looks like a temporary / swap file.

    Patterns matched:
    - Files starting with ``~`` (Office temp files)
    - Files starting with ``.`` (Unix hidden / swap)
    - Files ending with ``.tmp``, ``.temp``, ``.swp``, ``.swx``
    """
    name = Path(path).name
    if name.startswith("~") or name.startswith("."):
        return True
    suffix = get_file_extension(path)
    return suffix in {".tmp", ".temp", ".swp", ".swx", ".bak"}


def ensure_directory(path: Union[str, Path]) -> Path:
    """Create the directory if it does not exist and return the *Path*.

    Parameters
    ----------
    path : str or Path
        Directory path to ensure exists.

    Returns
    -------
    Path
        The resolved directory path.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
