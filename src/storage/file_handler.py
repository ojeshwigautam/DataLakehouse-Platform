from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from .storage_factory import StorageFactory


class FileHandler:
    @staticmethod
    def read(path: Union[str, Path], **kwargs) -> pd.DataFrame:
        handler = StorageFactory.get_handler(path)
        return handler.read(path, **kwargs)

    @staticmethod
    def write(df: pd.DataFrame, path: Union[str, Path], **kwargs) -> None:
        handler = StorageFactory.get_handler(path)
        handler.write(df, path, **kwargs)
