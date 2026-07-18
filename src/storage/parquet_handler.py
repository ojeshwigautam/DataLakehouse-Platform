from __future__ import annotations

import shutil

from pathlib import Path
from typing import Union

import pandas as pd


class ParquetHandler:
    @staticmethod
    def read(path: Union[str, Path], **kwargs) -> pd.DataFrame:
        path = Path(path)
        return pd.read_parquet(path, **kwargs)

    @staticmethod
    def write(df: pd.DataFrame, path: Union[str, Path], **kwargs) -> None:
        path = Path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        # Remove existing file or directory
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

        df.to_parquet(
            path,
            engine="pyarrow",
            compression="snappy",
            index=False,
            **kwargs,
        )
