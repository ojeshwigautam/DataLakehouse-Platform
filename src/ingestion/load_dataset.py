from pathlib import Path

from src.storage.file_handler import FileHandler

from src.utils.logger import logger



from src.config.settings import RAW_DATASET


def load_dataset(dataset_path=RAW_DATASET):
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

    logger.info(f"Loading dataset from {dataset_path}")

    df = FileHandler.read(dataset_path)

    # Remove accidental index column
    if "Unnamed: 0" in df.columns:
        df.drop(columns=["Unnamed: 0"], inplace=True)

    logger.info("Dataset loaded successfully")
    logger.info(f"Rows    : {df.shape[0]}")
    logger.info(f"Columns : {df.shape[1]}")

    return df

