from __future__ import annotations

from pathlib import Path

from .csv_handler import CsvHandler
from .parquet_handler import ParquetHandler


class StorageFactory:
    @staticmethod
    def get_handler(path: str | Path):
        path = Path(path)
        suffix = path.suffix.lower()

        if suffix == ".csv":
            return CsvHandler

        # Accept a couple of common parquet extensions.
        if suffix in {".parquet", ".pq"}:
            return ParquetHandler

        raise ValueError(f"Unsupported file type for storage: {suffix} ({path})")

