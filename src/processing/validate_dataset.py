import pandas as pd


def validate_dataset(df: pd.DataFrame):
    """
    Validate dataset quality before processing.
    """

    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)

    print(f"\nRows : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    duplicate_rows = df.duplicated().sum()

    print(f"\nDuplicate Rows : {duplicate_rows}")

    missing_values = df.isnull().sum().sum()

    print(f"Missing Values : {missing_values}")

    print("\nData Types")

    print("-" * 60)

    print(df.dtypes)

    print("\nValidation Completed Successfully")

