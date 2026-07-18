from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd


class CsvHandler:
    @staticmethod
    def read(path: Union[str, Path], **kwargs) -> pd.DataFrame:
        path = Path(path)
        return pd.read_csv(
    path,
    low_memory=False,
    **kwargs
)

    @staticmethod
    def write(df: pd.DataFrame, path: Union[str, Path], **kwargs) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Default behavior matches prior code paths in this repo.
        if "index" not in kwargs:
            kwargs["index"] = False

        df.to_csv(path, **kwargs)

