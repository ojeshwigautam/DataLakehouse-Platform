from pathlib import Path

import pandas as pd


def load_dataset(dataset_path):
    """Load the historical dataset.

    Parameters
    ----------
    dataset_path : str or Path
        Path to the CSV file.

    Returns
    -------
    pandas.DataFrame
    """

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    print(f"Loading dataset from {dataset_path}")

    df = pd.read_csv(dataset_path)

    # Remove accidental index column
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    print("Dataset loaded successfully")
    print(f"Rows    : {df.shape[0]}")
    print(f"Columns : {df.shape[1]}")

    return df

