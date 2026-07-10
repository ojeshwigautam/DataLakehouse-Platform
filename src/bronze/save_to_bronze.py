from pathlib import Path
import pandas as pd


def save_to_bronze(df: pd.DataFrame, output_dir):
    """
    Save the raw dataframe into Bronze Layer.
    """

    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "bronze_orders.csv"

    df.to_csv(output_file, index=False)

    print("=" * 60)
    print("Bronze Layer Created Successfully")
    print(f"Saved to : {output_file}")
    print("=" * 60)

