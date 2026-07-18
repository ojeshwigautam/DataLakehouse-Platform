from __future__ import annotations

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

        df.to_parquet(
    path,
    engine="pyarrow",
    compression="snappy",
    index=False,
    **kwargs
)