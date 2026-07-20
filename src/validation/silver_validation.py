import pandas as pd
import pandera as pa
from pandera import Check

from src.validation.validation_utils import save_validation_report


SilverSchema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(str, nullable=False),
        "order_item_id": pa.Column(int, nullable=False),
        "customer_id": pa.Column(str, nullable=False),
        "product_id": pa.Column(str, nullable=False),
        "seller_id": pa.Column(str, nullable=False),

        "price": pa.Column(
            float,
            Check.ge(0),
            nullable=False
        ),

        "freight_value": pa.Column(
            float,
            Check.ge(0),
            nullable=False
        ),

        "payment_value": pa.Column(
            float,
            Check.ge(0),
            nullable=False
        ),

        "order_purchase_timestamp": pa.Column(
            str,
            nullable=False
        ),

        "order_status": pa.Column(
            str,
            nullable=False
        )
    },
    strict=False,
    coerce=True
)


def validate_silver(file_path):

    df = pd.read_csv(file_path)

    if len(df) < 100000:
        save_validation_report(
            "silver",
            False,
            f"Unexpected row count: {len(df)}"
        )
        raise ValueError(
            "Silver dataset row count is lower than expected."
        )

    SilverSchema.validate(df)

    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        save_validation_report(
            "silver",
            False,
            f"{duplicate_rows} exact duplicate rows found."
        )
        raise ValueError("Exact duplicate rows detected.")

    allowed_status = {
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable"
    }

    invalid = ~df["order_status"].isin(allowed_status)

    if invalid.any():
        save_validation_report(
            "silver",
            False,
            "Invalid order_status values found."
        )
        raise ValueError(
            "Invalid order_status values detected."
        )

    save_validation_report(
        "silver",
        True,
        "Silver validation passed successfully."
    )

    print("✅ Silver validation passed.")


if __name__ == "__main__":
    validate_silver(
        "data/silver/silver_orders.csv"
    )

