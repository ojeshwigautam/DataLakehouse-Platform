"""
File Discovery Service — Scans the incremental folder for supported files.

Responsibilities
----------------
- Scan the configured ``data/raw/incremental/`` directory.
- Detect supported file formats (``.csv``, ``.parquet``, ``.json``).
- Ignore hidden / temporary files.
- Sort files by modification time (newest first).
- Return file paths for downstream processing.

Usage::

    from src.ingestion.file_discovery import FileDiscoverer

    discoverer = FileDiscoverer()
    files      = discoverer.discover_files()       # all new files
    latest     = discoverer.get_latest_file()       # most recent only
"""

from pathlib import Path
from typing import List, Optional, Union

from src.config.settings import INCREMENTAL_DATA_DIR
from src.utils.file_utils import is_hidden_file, is_supported_format, is_temp_file
from src.utils.logger import logger


class FileDiscoverer:
    """Discover supported data files in the incremental ingestion folder.

    Parameters
    ----------
    base_path : str or Path, optional
        Directory to scan.  Defaults to ``data/raw/incremental/``
        from settings.
    """

    def __init__(
        self,
        base_path: Optional[Union[str, Path]] = None,
    ):
        self.base_path = Path(base_path or INCREMENTAL_DATA_DIR)

        if not self.base_path.exists():
            logger.warning(
                f"Incremental data directory does not exist: " f"{self.base_path}"
            )
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created incremental data directory: {self.base_path}")

    # ── Core discovery ─────────────────────────────────────────────

    def discover_files(
        self,
        sort_by: str = "mtime",
        reverse: bool = True,
    ) -> List[Path]:
        """Scan the base path and return valid, ingestible file paths.

        Parameters
        ----------
        sort_by : str
            Attribute to sort by (``"mtime"``, ``"name"``, ``"size"``).
        reverse : bool
            When *True* (default) returns newest / largest / Z–A first.
            Set to *False* for oldest / smallest / A–Z first.

        Returns
        -------
        List[Path]
            Sorted list of file paths ready for ingestion.
        """
        if not self.base_path.is_dir():
            logger.warning(f"Base path is not a directory: {self.base_path}")
            return []

        candidates: List[Path] = []

        for child in self.base_path.iterdir():
            if not child.is_file():
                continue
            if is_hidden_file(child) or is_temp_file(child):
                logger.debug(f"Ignoring hidden/temp file: {child.name}")
                continue
            if not is_supported_format(child):
                logger.debug(
                    f"Ignoring unsupported format: {child.name} "
                    f"(extension={child.suffix})"
                )
                continue
            candidates.append(child)

        sorted_files = self.sort_files(candidates, by=sort_by, reverse=reverse)

        logger.info(
            f"Discovered {len(sorted_files)} file(s) in " f"'{self.base_path.name}'"
        )
        for fp in sorted_files:
            logger.debug(f"  └── {fp.name}")

        return sorted_files

    # ── Latest file helper ─────────────────────────────────────────

    def get_latest_file(
        self,
        sort_by: str = "mtime",
    ) -> Optional[Path]:
        """Return the single most recent (or largest) file.

        Parameters
        ----------
        sort_by : str
            ``"mtime"`` (default), ``"name"``, or ``"size"``.

        Returns
        -------
        Path or None
            The latest file, or *None* if the folder is empty.
        """
        files = self.discover_files(sort_by=sort_by, reverse=True)
        return files[0] if files else None

    # ── Sorting ────────────────────────────────────────────────────

    @staticmethod
    def sort_files(
        files: List[Path],
        by: str = "mtime",
        reverse: bool = True,
    ) -> List[Path]:
        """Sort a list of file paths.

        Parameters
        ----------
        files : List[Path]
            File paths to sort.
        by : str
            Sort key — ``"mtime"`` (modification time), ``"name"``, or
            ``"size"``.
        reverse : bool
            Descending order when *True*.

        Returns
        -------
        List[Path]
            Sorted list.
        """
        key_map = {
            "mtime": lambda p: p.stat().st_mtime,
            "name": lambda p: p.name,
            "size": lambda p: p.stat().st_size,
        }

        key_func = key_map.get(by)
        if key_func is None:
            logger.warning(f"Unknown sort key '{by}', falling back to 'mtime'")
            key_func = key_map["mtime"]

        return sorted(files, key=key_func, reverse=reverse)

    # ── Filename validation ────────────────────────────────────────

    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Check whether the filename follows the expected convention.

        The expected pattern is: ``<prefix>_<YYYY_MM_DD>.csv``

        This is a lightweight validation that ensures basic naming
        hygiene.  Override or extend as needed for domain-specific rules.

        Parameters
        ----------
        filename : str
            Name of the file (not the full path).

        Returns
        -------
        bool
            ``True`` if the name looks valid.
        """
        import re

        # Accept snake_case names with an optional date suffix
        pattern = r"^[a-zA-Z0-9_]+(_\d{4}_\d{2}_\d{2})?\.[a-z]+$"
        return bool(re.match(pattern, filename))
